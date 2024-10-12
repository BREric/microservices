from pymongo import MongoClient
import os

def init_db():
    client = MongoClient(os.environ['MONGO_URI'])
    db = client[os.environ['MONGO_DB']]
    return db

db = init_db()