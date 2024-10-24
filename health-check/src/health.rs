use actix_web::{get, web, HttpResponse, Responder};
use chrono::{DateTime, Utc};
use serde::Serialize;
use std::sync::{Arc, Mutex};
use std::time::Instant;

use crate::utils::AppState;

// Estructura para la respuesta de los checks de salud
#[derive(Serialize)]
struct HealthResponse {
    status: String,
    checks: Vec<Check>,
}

#[derive(Serialize)]
struct Check {
    name: String,
    status: String,
    data: CheckData,
}

#[derive(Serialize)]
struct CheckData {
    from: DateTime<Utc>,
    status: String,
}

// Convertimos el tiempo de ejecución a una fecha
fn get_uptime_data(start_time: Instant, status: &str) -> CheckData {
    let uptime_duration = start_time.elapsed();
    let now = Utc::now() - chrono::Duration::from_std(uptime_duration).unwrap();
    CheckData {
        from: now,
        status: status.to_string(),
    }
}

// Ruta para `/health`
#[get("/health")]
async fn health(data: web::Data<Arc<Mutex<AppState>>>) -> impl Responder {
    let start_time = data.lock().unwrap().start_time;
    let health_response = HealthResponse {
        status: "UP".to_string(),
        checks: vec![
            Check {
                name: "Readiness check".to_string(),
                status: "UP".to_string(),
                data: get_uptime_data(start_time, "READY"),
            },
            Check {
                name: "Liveness check".to_string(),
                status: "UP".to_string(),
                data: get_uptime_data(start_time, "ALIVE"),
            },
        ],
    };
    HttpResponse::Ok().json(health_response)
}

// Ruta para `/health/ready`
#[get("/health/ready")]
async fn readiness(data: web::Data<Arc<Mutex<AppState>>>) -> impl Responder {
    let start_time = data.lock().unwrap().start_time;
    let readiness_check = Check {
        name: "Readiness check".to_string(),
        status: "UP".to_string(),
        data: get_uptime_data(start_time, "READY"),
    };
    HttpResponse::Ok().json(readiness_check)
}

// Ruta para `/health/live`
#[get("/health/live")]
async fn liveness(data: web::Data<Arc<Mutex<AppState>>>) -> impl Responder {
    let start_time = data.lock().unwrap().start_time;
    let liveness_check = Check {
        name: "Liveness check".to_string(),
        status: "UP".to_string(),
        data: get_uptime_data(start_time, "ALIVE"),
    };
    HttpResponse::Ok().json(liveness_check)
}
