import os

import pika
from flask import Blueprint, jsonify
from pymongo import MongoClient
from pika.exceptions import AMQPConnectionError

health_blueprint = Blueprint('health_blueprint', __name__)

def check_mongo():
    """
    Verifica la conexión a MongoDB.
    """
    try:
        mongo_client = MongoClient(os.getenv('MONGO_URI'))
        mongo_client.server_info()  # Si no lanza una excepción, Mongo está disponible
        return {"name": "MongoDB", "status": "UP", "data": "MongoDB is reachable"}
    except Exception as e:
        return {"name": "MongoDB", "status": "DOWN", "data": str(e)}

def check_rabbitmq():
    """
    Verifica la conexión a RabbitMQ.
    """
    try:
        connection_params = pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost'))
        connection = pika.BlockingConnection(connection_params)
        connection.close()
        return {"name": "RabbitMQ", "status": "UP", "data": "RabbitMQ is reachable"}
    except AMQPConnectionError as e:
        return {"name": "RabbitMQ", "status": "DOWN", "data": str(e)}

@health_blueprint.route('/health', methods=['GET'])
def health():
    """
    Endpoint de Health Check para verificar el estado de MongoDB y RabbitMQ.
    """
    health_status = {
        "status": "UP",
        "checks": [
            check_mongo(),
            check_rabbitmq()
        ],
        "data": {
            "from": "Health Check Endpoint",
            "status": "ALIVE"
        }
    }

    return jsonify(health_status), 200
