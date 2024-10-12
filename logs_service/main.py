from flask import Flask
from app.routes import log_blueprint
from app.database import db

app = Flask(__name__)

app.register_blueprint(log_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)