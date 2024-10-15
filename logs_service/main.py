import threading
import time
import logging
import sys
from flask import Flask
from app.routes import log_blueprint
from app.consumer import RabbitMQConsumer

# Configuración básica de logging para asegurarnos de que los mensajes se impriman a stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Enviar logs a stdout
    ]
)

app = Flask(__name__)

# Registrar las rutas
app.register_blueprint(log_blueprint)

def run_consumer():
    """
    Función que se ejecuta en un hilo separado para consumir mensajes de RabbitMQ.
    """
    logging.info("Starting RabbitMQ consumer thread...")
    consumer = RabbitMQConsumer(rabbitmq_host='rabbitmq', queue_name='logs_queue')
    while True:
        logging.info("Attempting to consume logs from RabbitMQ...")
        consumer.consume_logs()
        time.sleep(5)  # Espera 5 segundos antes de volver a intentar

def start_consumer_thread():
    """
    Función para iniciar el hilo del consumidor de RabbitMQ.
    """
    logging.info("Iniciando el hilo del consumidor de RabbitMQ...")
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    logging.info("El hilo del consumidor de RabbitMQ se inició correctamente.")

if __name__ == '__main__':
    start_consumer_thread()
    app.run(host='0.0.0.0', port=5000)