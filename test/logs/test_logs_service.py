import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/logs"

# Prueba para la creación de un log
def test_create_log():
    payload = {
        "app_name": "UserManagementApp",
        "log_type": "INFO",
        "module": "User Module",
        "summary": "User Created",
        "description": "User was successfully created.",
    }

    response = requests.post(BASE_URL, json=payload)

    assert response.status_code == 201
    assert response.json().get("message") == "Log created"
    assert "log_id" in response.json()

# Prueba para la creación fallida de un log por campos faltantes
def test_create_log_missing_fields():
    payload = {
        "app_name": "UserManagementApp",
        "log_type": "ERROR",
        # Faltan "module", "summary", "description"
    }

    response = requests.post(BASE_URL, json=payload)

    assert response.status_code == 400
    assert "Missing required fields" in response.json().get("error")

# Prueba para la obtención de logs con filtros
def test_get_logs():
    params = {
        "app_name": "UserManagementApp",
        "log_type": "INFO",
        "start_date": datetime.now().isoformat(),
        "end_date": datetime.now().isoformat(),
        "page": 1,
        "page_size": 10
    }

    response = requests.get(BASE_URL, params=params)

    assert response.status_code == 200
    logs = response.json()

    assert isinstance(logs, list)

    if logs:
        log = logs[0]
        assert "app_name" in log
        assert "log_type" in log
        assert "created_at" in log

# Prueba de paginación
def test_get_logs_pagination():
    params = {
        "page": 1,
        "page_size": 5
    }

    response = requests.get(BASE_URL, params=params)

    assert response.status_code == 200
    logs = response.json()

    assert len(logs) <= 5
