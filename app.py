import flask
import flask_jwt_extended as JWT
import functools
import redis

from redis.lock import Lock as RedisLock
from pydantic.error_wrappers import ValidationError
from flask import Flask
from datetime import timedelta
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import orm
from loguru import logger
from pyotp import TOTP

from src.config import AppConfig
from src import dto, model
from src.background import BackgroundJobExecutor
from src.demo_data import reset_to_demo_data
from src.passhash import verify_password

REDIS_LOCK_TIMEOUT = 600

logger.level("INFO")
config = AppConfig()
job_executor = BackgroundJobExecutor()
redis_client = redis.Redis.from_url(config.redis_uri)

app = Flask(__name__, static_folder="dist/")
app.config["JWT_SECRET_KEY"] = config.secret_key

CORS(app)
JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.db_uri
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_size": 5, "echo": True}

model.db.init_app(app)


@app.errorhandler(ValidationError)
def handle_exception(e: ValidationError):
    return ({"detail": str(e)}, 422)


def with_user(scopes: list[str] | None | str = None):
    if isinstance(scopes, str):
        scopes = [scopes]
    scopes = scopes or []

    def _with_user_wrapper(fn):
        @functools.wraps(fn)
        def decorate(*args, **kwargs):
            user_id = JWT.get_jwt_identity()

            full_jwt = JWT.get_jwt()
            jwt_scopes = full_jwt.get("scopes")
            trusted_app_id = full_jwt.get("trusted_app_id")

            if len(scopes) > 0 and jwt_scopes != "*":
                if jwt_scopes is None or len(
                    set(scopes).intersection(jwt_scopes)
                ) < len(scopes):
                    # If the token's scopes do not cover the required scopes, return a 401 error
                    return dict(detail="INSUFFICIENT_SCOPE"), 401

            user = model.db.session.scalars(
                model.db.select(model.User).where(model.User.id == user_id)
            ).first()

            if user is None:
                return dict(detail="INVALID_TOKEN"), 400

            flask.g.user = user
            flask.g.token_scopes = jwt_scopes
            flask.g.trusted_app_id = trusted_app_id

            return fn(*args, **kwargs)

        return decorate

    return _with_user_wrapper


def with_trusted_app():
    def _with_trusted_app_wrapper(fn):
        @functools.wraps(fn)
        def decorate(*args, **kwargs):
            app_id = flask.request.headers.get("x-app-id", None)
            app_secret = flask.request.headers.get("x-app-secret", None)

            if app_id is None or app_secret is None:
                return {"detail": "MISSING_AUTH_HEADER"}, 401

            app = model.db.session.scalars(
                model.db.select(model.TrustedApp).where(model.TrustedApp.id == app_id)
            ).first()

            if app is None:
                return {"detail": "INVALID_CREDENTIALS"}, 401

            if not verify_password(app_secret, app.secret_key_hash):
                return {"detail": "INVALID_CREDENTIALS"}, 401

            flask.g.trusted_app = app

            return fn(*args, **kwargs)
        return decorate
    return _with_trusted_app_wrapper

# API routes


@app.get("/api/users/search")
@with_trusted_app()
def search_users():
    phone = flask.request.args.get("phone")
    has_phone = phone is not None

    if not has_phone:
        return {"detail": "MISSING_QUERY"}, 400

    user = model.db.session.scalars(
        model.db.select(model.User).where(model.User.phone == phone)
    ).first()

    if user is None:
        return {"detail": "NO_USER_FOUND"}, 404

    return dto.UserInfoDto.from_db_model(user).dict()


@app.post("/api/trusted-app/impersonate")
@with_trusted_app()
def impersonate_user():
    user_id = flask.request.args.get("user_id", type=int)
    if user_id is None:
        return {"detail": "MISSING_ID"}, 400

    user = model.db.session.scalars(
        model.db.select(model.User).where(model.User.id == user_id)
    ).first()
    if user is None:
        return {"detail": "INVALID_ID"}, 400

    token = JWT.create_access_token(
        identity=user_id,
        expires_delta=timedelta(minutes=20),
        additional_claims={
            "scopes": ["transactions/submit", "me/accounts"],
            "trusted_app_id": flask.g.trusted_app.id
        }
    )

    return dto.LoginResponse(token=token).dict()


@app.post("/api/transactions/submit")
@JWT.jwt_required()
@with_user("transactions/submit")
def submit_transaction():
    payload = dto.TransactionSubmitRequest.parse_obj(flask.request.json)

    from_account = model.db.session.scalars(
        model.db.select(model.UserAccount).where(
            model.UserAccount.id == payload.from_account_id
        )
    ).first()
    to_account = model.db.session.scalars(
        model.db.select(model.UserAccount).where(
            model.UserAccount.id == payload.to_account_id
        )
    ).first()

    if from_account is None or to_account is None:
        return dict(detail="INVALID_ACCOUNT_IDS"), 400

    # Check source account for ownership
    if from_account.user_id != flask.g.user.id:
        return dict(detail="INVALID_SOURCE_ID"), 401

    # Validate PIN
    if not verify_password(payload.pin, flask.g.user.pin_hash):
        return dict(detail="INCORRECT_PIN"), 401

    if flask.g.user.totp_key is not None:
        # Validate TOTP
        totp_handler = TOTP(flask.g.user.totp_key)
        if not totp_handler.verify(payload.totp_token):
            return dict(detail="INVALID_TOTP"), 401

    # Lock both accounts to avoid race conditions
    with RedisLock(
        redis_client,
        f"accounts/{from_account.id}",
        timeout=REDIS_LOCK_TIMEOUT,
        blocking=True,
        blocking_timeout=30,
    ), RedisLock(
        redis_client,
        f"accounts/{to_account.id}",
        timeout=REDIS_LOCK_TIMEOUT,
        blocking=True,
        blocking_timeout=30,
    ):
        # Check remaining balance
        if from_account.balance < payload.amount:
            return dict(detail="INSUFFICIENT_BALANCE"), 400

        # Perform transaction
        transaction = model.Transaction(
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            description=payload.description,
            status="success",
            trusted_app_id=flask.g.trusted_app_id,
        )
        model.db.session.add(transaction)
        from_account.balance = from_account.balance - payload.amount
        to_account.balance = to_account.balance + payload.amount
        model.db.session.commit()
        model.db.session.refresh(transaction)

        return dto.TransactionDto.from_db_model_plain(transaction).dict(
            exclude_none=True
        )


@app.get("/api/accounts/search")
@JWT.jwt_required()
@with_user("accounts/search")
def user_search_accounts():
    return search_accounts()


@app.get("/api/trusted-app/accounts/search")
@with_trusted_app()
def tapp_search_accounts():
    return search_accounts()


def search_accounts():
    phone = flask.request.args.get("phone")
    bank_id = flask.request.args.get("bank_id", type=int)
    bank_account_number = flask.request.args.get("bank_account", type=str)
    bank_card_number = flask.request.args.get("bank_card", type=str)

    has_bank_account = (bank_id is not None) and (bank_account_number is not None)
    has_bank_card = (bank_id is not None) and (bank_card_number is not None)
    has_phone = phone is not None
    if not (has_bank_account or has_bank_card or has_phone):
        return dict(detail="MISSING_QUERY"), 400

    query = model.db.select(
        model.UserAccount.id, model.UserAccount.user_id, model.UserAccount.type
    ).join(model.User, model.UserAccount.user_id == model.User.id)

    if has_phone:
        query = query.where(model.User.phone == phone)
    elif has_bank_account:
        query = query.where(
            (model.UserAccount.bank_id == bank_id)
            & (model.UserAccount.bank_account_number == bank_account_number)
        )
    elif has_bank_card:
        query = query.where(
            (model.UserAccount.bank_id == bank_id)
            & (model.UserAccount.bank_card_number == bank_card_number)
        )

    query = query.limit(1)
    account = model.db.session.execute(query).first()

    if account is None:
        return dict(detail="ACCOUNT_NOT_FOUND"), 404

    return dto.AccountDto.from_db_model_private(account).dict(exclude_unset=True)


@app.route("/api/login", methods=["POST"])
def login():
    req = dto.LoginRequest.parse_obj(flask.request.json)
    matched_user = model.db.session.scalars(
        model.db.select(model.User).where(model.User.phone == req.phone)
    ).first()

    if matched_user is None:
        return dict(detail="INVALID_LOGIN"), 401

    pass_hash = matched_user.password_hash
    if not verify_password(req.password, pass_hash):
        return dict(detail="INVALID_LOGIN"), 401

    access_token = JWT.create_access_token(
        identity=matched_user.id,
        additional_claims={"scopes": "*"},
        expires_delta=timedelta(days=7),
    )
    return dto.LoginResponse(token=access_token).dict()


@app.get("/api/users/me/info")
@JWT.jwt_required()
@with_user("me/info")
def get_current_user_info():
    current_user = flask.g.user
    return dto.UserInfoDto.from_db_model(current_user).dict()


@app.get("/api/users/me/accounts")
@JWT.jwt_required()
@with_user("me/accounts")
def get_current_user_accounts():
    limit = flask.request.args.get("limit", 10)

    current_user = flask.g.user
    accounts = model.db.session.scalars(
        model.db.select(model.UserAccount)
        .where(model.UserAccount.user_id == current_user.id)
        .order_by(model.UserAccount.priority.desc())
        .limit(limit)
    ).all()

    return dto.AccountListDto(
        items=[dto.AccountDto.from_db_model(item) for item in accounts]
    ).dict()


@app.get("/api/users/me/transactions/outgoing")
@JWT.jwt_required()
@with_user("me/transactions")
def get_current_user_transactions_outgoing():
    limit = flask.request.args.get("limit", 20)
    offset = flask.request.args.get("limit", 0)

    current_user = flask.g.user

    account1 = orm.aliased(model.UserAccount)
    account2 = orm.aliased(model.UserAccount)
    user1 = orm.aliased(model.User)
    user2 = orm.aliased(model.User)

    transactions = model.db.session.execute(
        model.db.select(
            model.Transaction.id,
            model.Transaction.from_account_id,
            model.Transaction.to_account_id,
            model.Transaction.amount,
            model.Transaction.description,
            model.Transaction.status,
            model.Transaction.created_at,
            model.Transaction.trusted_app_id,
            user1.name.label("from_user_name"),
            user2.name.label("to_user_name"),
        )
        .join(account1, model.Transaction.from_account_id == account1.id)
        .join(account2, model.Transaction.to_account_id == account2.id)
        .join(user1, account1.user_id == user1.id)
        .join(user2, account2.user_id == user2.id)
        .where(
            (account1.user_id == current_user.id)
            & (model.Transaction.status == "success")
        )
        .order_by(model.Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return dto.TransactionListDto(
        items=[dto.TransactionDto.from_db_model(item) for item in transactions]
    ).dict()


@app.get("/api/users/me/transactions/incoming")
@JWT.jwt_required()
@with_user("me/transactions")
def get_current_user_transactions_incoming():
    limit = flask.request.args.get("limit", 20)
    offset = flask.request.args.get("limit", 0)

    current_user = flask.g.user

    account1 = orm.aliased(model.UserAccount)
    account2 = orm.aliased(model.UserAccount)
    user1 = orm.aliased(model.User)
    user2 = orm.aliased(model.User)

    transactions = model.db.session.execute(
        model.db.select(
            model.Transaction.id,
            model.Transaction.from_account_id,
            model.Transaction.to_account_id,
            model.Transaction.amount,
            model.Transaction.description,
            model.Transaction.status,
            model.Transaction.created_at,
            model.Transaction.trusted_app_id,
            user1.name.label("from_user_name"),
            user2.name.label("to_user_name"),
        )
        .join(account1, model.Transaction.from_account_id == account1.id)
        .join(account2, model.Transaction.to_account_id == account2.id)
        .join(user1, account1.user_id == user1.id)
        .join(user2, account2.user_id == user2.id)
        .where(
            (account2.user_id == current_user.id)
            & (model.Transaction.status == "success")
        )
        .order_by(model.Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return dto.TransactionListDto(
        items=[dto.TransactionDto.from_db_model(item) for item in transactions]
    ).dict()


@app.get("/api/users/me/transactions/all")
@JWT.jwt_required()
@with_user("me/transactions")
def get_current_user_transactions_all():
    limit = flask.request.args.get("limit", 20)
    offset = flask.request.args.get("limit", 0)

    current_user = flask.g.user

    account1 = orm.aliased(model.UserAccount)
    account2 = orm.aliased(model.UserAccount)
    user1 = orm.aliased(model.User)
    user2 = orm.aliased(model.User)

    transactions = model.db.session.execute(
        model.db.select(
            model.Transaction.id,
            model.Transaction.from_account_id,
            model.Transaction.to_account_id,
            model.Transaction.amount,
            model.Transaction.description,
            model.Transaction.status,
            model.Transaction.created_at,
            model.Transaction.trusted_app_id,
            user1.name.label("from_user_name"),
            user2.name.label("to_user_name"),
        )
        .join(account1, model.Transaction.from_account_id == account1.id)
        .join(account2, model.Transaction.to_account_id == account2.id)
        .join(user1, account1.user_id == user1.id)
        .join(user2, account2.user_id == user2.id)
        .where(
            (
                (account1.user_id == current_user.id)
                | (account2.user_id == current_user.id)
            )
            & (model.Transaction.status == "success")
        )
        .order_by(model.Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return dto.TransactionListDto(
        items=[dto.TransactionDto.from_db_model(item) for item in transactions]
    ).dict()


# Utility routes


@app.route("/api/debug/demo-data", methods=["POST"])
def reset_data():
    reset_to_demo_data()
    return "OK", 200


@app.route("/")
def homepage():
    return app.send_static_file("index.html")


@app.route("/<path:path>")
def serve_static_file(path):
    return app.send_static_file(path)


@app.route("/health")
def healthcheck():
    return ("OK", 200)
