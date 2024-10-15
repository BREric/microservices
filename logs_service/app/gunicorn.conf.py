import os

def on_starting(server):
    # Ejecutar el código que estás ejecutando en el archivo main.py
    from main import start_consumer_thread
    start_consumer_thread()