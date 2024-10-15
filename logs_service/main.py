from flask import Flask
from app.routes import log_blueprint
from app.database import db
import threading
from app.consumer import run_consumer
import app.consumer  # Agrega esta línea

app = Flask(__name__)

app.register_blueprint(log_blueprint)

if __name__ == '__main__':
    thread = threading.Thread(target=run_consumer)
    thread.daemon = True  # Esto permite que el thread se detenga cuando se detenga la aplicación
    thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)