import pika
import logging
import time
from datetime import datetime
import json  # Asegúrate de importar json

class RabbitMQConsumer:
    def __init__(self, rabbitmq_host='localhost', queue_name='logs', retry_interval=5):
        """
        Inicializa el consumidor de RabbitMQ.
        :param rabbitmq_host: Host de RabbitMQ
        :param queue_name: Nombre de la cola en RabbitMQ
        :param retry_interval: Intervalo para reintentar la conexión en segundos
        """
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.retry_interval = retry_interval
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Conectar a RabbitMQ y configurar el canal y la cola.
        Si falla la conexión, reintenta después de `retry_interval` segundos.
        """
        while self.connection is None:
            try:
                logging.info(f"Attempting to connect to RabbitMQ at {self.rabbitmq_host}...")
                connection_params = pika.ConnectionParameters(host=self.rabbitmq_host)
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()

                # Asegurarse de que la cola exista
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                logging.info(f"Connected to RabbitMQ on {self.rabbitmq_host} and queue '{self.queue_name}' is ready.")
            except Exception as e:
                logging.error(f"Error connecting to RabbitMQ: {e}")
                logging.info(f"Retrying connection in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)

    def consume_logs(self):
        """
        Consumir mensajes de RabbitMQ. Este método es llamado en cada iteración del hilo de consumo.
        Si el canal no está disponible, intenta reconectar.
        """
        if self.channel is None:
            logging.warning("Channel not available. Trying to reconnect...")
            self.connect()

        if self.channel is not None:
            try:
                logging.info("Waiting for messages from RabbitMQ...")
                self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
                # Inicia el bucle de eventos de RabbitMQ
                self.connection.process_data_events()
            except Exception as e:
                logging.error(f"Error while consuming logs: {e}")
                self.connection = None
                self.channel = None
                logging.info("Retrying connection in the next iteration...")

    def callback(self, ch, method, properties, body):
        """
        Callback para procesar el mensaje de log.
        """
        log_data = body.decode('utf-8')
        self.process_log(log_data)
        ch.basic_ack(method.delivery_tag)  # Confirmar el procesamiento del mensaje

    def process_log(self, log_data):
        """
        Lógica para procesar el mensaje de log y guardarlo en MongoDB.
        """
        logging.info(f"Received message from RabbitMQ: {log_data}")
        
        # Intentar parsear el log como JSON
        try:
            log_data_json = json.loads(log_data)
        except json.JSONDecodeError:
            logging.error(f"Error parsing log data as JSON: {log_data}")
            return
        
        # Insertar el log en MongoDB
        try:
            from app.database import db  # Importar dentro de la función para evitar problemas de importación cíclica
            log_entry = {
                "app_name": log_data_json.get("app_name", ""),
                "log_type": log_data_json.get("log_type", ""),
                "module": log_data_json.get("module", ""),
                "created_at": datetime.utcnow(),
                "summary": log_data_json.get("summary", ""),
                "description": log_data_json.get("description", ""),
            }
            db.logs.insert_one(log_entry)
            logging.info(f"Log inserted into MongoDB: {log_data}")
        except Exception as e:
            logging.error(f"Failed to insert log into MongoDB: {e}")

    def close_connection(self):
        """
        Cerrar la conexión a RabbitMQ cuando sea necesario.
        """
        if self.connection is not None:
            self.connection.close()
            logging.info("RabbitMQ connection closed.")