from flask import Blueprint, request, jsonify
from app.database import db
from .models import LogModel
from datetime import datetime

log_blueprint = Blueprint('log_blueprint', __name__)

logs_model = LogModel(db)

@log_blueprint.route('/logs', methods=['POST'])
def create_log():
    data = request.get_json()
    print(f"Datos recibidos: {data}")
    if data is None:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["app_name", "log_type", "summary", "description"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        log_id = logs_model.create_log(
            app_name=data['app_name'],
            log_type=data['log_type'],
            module=data['module'],
            summary=data['summary'],
            description=data['description']
        )
        return jsonify({"message": "Log created", "log_id": str(log_id)}), 201
    except Exception as e:
        print(f"Error creating log: {e}")
        return jsonify({"error": str(e)}), 500  

@log_blueprint.route('/logs', methods=['GET'])
def get_logs():
    filters = {
        "app_name": request.args.get("app_name"),
        "log_type": request.args.get("log_type"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }

    # Convertir fechas a formato adecuado si están presentes
    if filters['start_date']:
        try:
            filters['start_date'] = datetime.fromisoformat(filters['start_date'])
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use ISO format."}), 400

    if filters['end_date']:
        try:
            filters['end_date'] = datetime.fromisoformat(filters['end_date'])
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use ISO format."}), 400

    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
    except ValueError:
        return jsonify({"error": "Invalid page or page_size value."}), 400

    # Verificar que `page` y `page_size` sean válidos
    if page < 1 or page_size < 1:
        return jsonify({"error": "Page and page_size must be positive integers."}), 400

    try:
        logs = logs_model.get_logs(filters, page, page_size)
        # Convertir el cursor a una lista de diccionarios
        logs_list = []
        for log in logs:
            log_dict = {
                "_id": str(log["_id"]),
                "app_name": log.get("app_name", ""),
                "log_type": log.get("log_type", ""),
                "module": log.get("module", ""),
                "created_at": log.get("created_at", "").isoformat() if log.get("created_at", "") else "",
                "summary": log.get("summary", ""),
                "description": log.get("description", ""),
            }
            logs_list.append(log_dict)
        return jsonify(logs_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500