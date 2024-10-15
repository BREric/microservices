import pika
import json
from app.database import db
from app.models import LogModel
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)

def callback(ch, method, properties, body):
    try:
        log_data = json.loads(body)
        logging.info("Received message from RabbitMQ: %s", log_data)
        
        # Verify database connection
        try:
            db.ping()
            logging.info("Database connection established")
        except Exception as e:
            logging.error("Error establishing database connection: %s", e)
            return
        
        # Create log
        try:
            logs_model = LogModel(db)
            log_id = logs_model.create_log(
                app_name=log_data['app_name'],
                log_type=log_data['log_type'],
                module=log_data['module'],
                summary=log_data['summary'],
                description=log_data['description']
            )
            logging.info("Log created with ID: %s", log_id)
        except Exception as e:
            logging.error("Error creating log: %s", e)
            return
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error("Error processing message: %s", e)

def get_messages():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        logging.info("Connected to RabbitMQ")
    except Exception as e:
        logging.error("Error connecting to RabbitMQ: %s", e)
        return
    
    channel = connection.channel()
    try:
        channel.queue_declare(queue='logs_queue', durable=True)
        logging.info("Logs queue declared")
    except Exception as e:
        logging.error("Error declaring logs queue: %s", e)
        return
    
    try:
        method, properties, body = channel.basic_get(queue='logs_queue', auto_ack=False)
        if body:
            callback(channel, method, properties, body)
    except Exception as e:
        logging.error("Error getting message: %s", e)
    
    connection.close()

def run_consumer():
    while True:
        get_messages()
        time.sleep(5)