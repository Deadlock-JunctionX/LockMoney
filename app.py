import flask
import flask_jwt_extended as JWT

from pydantic.error_wrappers import ValidationError
from flask import Flask
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
    )
    return dto.LoginResponse(token=access_token).dict()


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
