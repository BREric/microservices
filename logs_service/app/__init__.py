import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your_secret_key")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongodb_container:27017/logs")

jwt = JWTManager(app)
mongo = PyMongo(app)

db = mongo.db  

from .routes import log_blueprint
app.register_blueprint(log_blueprint)

def create_app():
    return app