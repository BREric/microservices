from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

app.config["MONGO_URI"] = "mongodb://mongodb_container:27017/logs_service"
mongo = PyMongo(app)

client = MongoClient("mongodb://mongodb_container:27017")
db = client['logs_service']  

from .routes import log_blueprint
app.register_blueprint(log_blueprint)

def create_app():
    return app
