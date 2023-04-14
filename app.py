import flask
import flask_jwt_extended as JWT
import functools

from pydantic.error_wrappers import ValidationError
from flask import Flask
from datetime import timedelta
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy.pool import NullPool

from src.config import AppConfig
from src import dto, model
from src.background import BackgroundJobExecutor
from src.demo_data import reset_to_demo_data
from src.passhash import verify_password

config = AppConfig()
job_executor = BackgroundJobExecutor()

app = Flask(__name__, static_folder="dist/")
app.config["JWT_SECRET_KEY"] = config.secret_key

CORS(app)
JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.db_uri
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_size": 5}

model.db.init_app(app)


@app.errorhandler(ValidationError)
def handle_exception(e: ValidationError):
    return ({"detail": str(e)}, 422)


def with_user(fn):
    @functools.wraps(fn)
    def decorate(*args, **kwargs):
        user_id = JWT.get_jwt_identity()
        user = model.db.session.scalars(
            model.db.select(model.User).where(model.User.id == user_id)
        ).first()
        if user is None:
            return dict(detail="Invalid token"), 400

        flask.g.user = user
        return fn(*args, **kwargs)

    return decorate


# API routes


@app.route("/api/login", methods=["POST"])
def login():
    req = dto.LoginRequest.parse_obj(flask.request.json)
    matched_user = model.db.session.scalars(
        model.db.select(model.User).where(model.User.phone == req.phone)
    ).first()

    if matched_user is None:
        return dict(detail="Invalid login"), 401

    pass_hash = matched_user.password_hash
    if not verify_password(req.password, pass_hash):
        return dict(detail="Invalid login"), 401

    access_token = JWT.create_access_token(
        identity=matched_user.id,
        expires_delta=timedelta(days=7),
    )
    return dto.LoginResponse(token=access_token).dict()


@app.get("/api/users/me/info")
@JWT.jwt_required()
@with_user
def get_current_user_info():
    current_user = flask.g.user
    return dto.UserInfoDto(
        id=current_user.id,
        name=current_user.name,
        phone=current_user.phone
    ).dict()


@app.get("/api/users/me/accounts")
@JWT.jwt_required()
@with_user
def get_current_user_accounts():
    limit = flask.request.args.get("limit", 10)

    current_user = flask.g.user
    accounts = model.db.session.scalars(
        model.db.select(model.UserAccount).where(model.UserAccount.user_id == current_user.id).order_by(model.UserAccount.priority.desc()).limit(limit)
    ).all()

    return dto.AccountListDto(
        items=[
            dto.AccountDto(
                id=item.id,
                user_id=item.user_id,
                initial_balance=item.initial_balance,
                balance=item.balance,
                type=item.type,
                bank_id=item.bank_id,
                bank_account_number=item.bank_account_number,
                bank_card_number=item.bank_card_number,
                priority=item.priority,
            )
            for item in accounts
        ]
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
