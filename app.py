from flask import Flask
from flask_cors import CORS

from src.config import AppConfig
from src.model import db

config = AppConfig()
app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = config.db_uri
db.init_app(app)

@app.route("/")
def homepage():
    return app.send_static_file("index.html")

@app.route("/<path:path>")
def serve_static_file(path):
    return app.send_static_file(path)


@app.route("/health")
def healthcheck():
    return ("OK", 200)
