from pymongo import MongoClient
from bson import ObjectId

class LogModel:
    def __init__(self, db):
        self.collection = db['logs']

    def create_log(self, log):
        self.collection.insert_one(log)
        return log

    def get_logs(self, filters, page, page_size):
        query = {}
        if filters.get('app_name'):
            query['app_name'] = filters['app_name']
        if filters.get('log_type'):
            query['log_type'] = filters['log_type']
        if filters.get('start_date') and filters.get('end_date'):
            query['created_at'] = {
                '$gte': filters['start_date'],
                '$lte': filters['end_date']
            }

        logs = self.collection.find(query).sort("created_at", -1)
        logs = logs.skip((page - 1) * page_size).limit(page_size)

        # Convertir los logs a un formato serializable
        return [{"id": str(log["_id"]), **log} for log in logs]