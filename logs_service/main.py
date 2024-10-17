import os
import threading
import time
import logging
import sys
from flask import Flask
from app.routes import log_blueprint
from app.consumer import RabbitMQConsumer

# Basic logging configuration to ensure messages are printed to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Send logs to stdout
    ]
)

app = Flask(__name__)

# Register routes
app.register_blueprint(log_blueprint)

def run_consumer():
    """
    Function that runs in a separate thread to consume messages from RabbitMQ.
    """
    logging.info("Starting RabbitMQ consumer thread...")
    rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
    queue_name = os.environ.get('RABBITMQ_QUEUE_NAME', 'logs_queue')
    consumer = RabbitMQConsumer(rabbitmq_host=rabbitmq_host, queue_name=queue_name)
    while True:
        logging.info("Attempting to consume logs from RabbitMQ...")
        consumer.consume_logs()
        time.sleep(5)  # Wait 5 seconds before trying again

def start_consumer_thread():
    """
    Function to start the RabbitMQ consumer thread.
    """
    logging.info("Starting RabbitMQ consumer thread...")
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    logging.info("RabbitMQ consumer thread started successfully.")

if __name__ == '__main__':
    start_consumer_thread()
    app.run(host='0.0.0.0', port=5000)