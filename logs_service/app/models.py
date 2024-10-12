from datetime import datetime

class LogModel:
    def __init__(self, db):
        self.collection = db['logs']

    def create_log(self, app_name, log_type, module, summary, description):
        log = {
            "app_name": app_name,
            "log_type": log_type,
            "module": module,
            "created_at": datetime.utcnow(),
            "summary": summary,
            "description": description,
        }
        result = self.collection.insert_one(log)
        return str(result.inserted_id)

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
        return logs.skip((page - 1) * page_size).limit(page_size)