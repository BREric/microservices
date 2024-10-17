import os

def on_starting(server):
    from main import start_consumer_thread
    start_consumer_thread()