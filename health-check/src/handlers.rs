use actix_web::{HttpResponse};
use reqwest;
use serde::Serialize;
use std::env;

#[derive(Serialize)]
struct ServiceStatus {
    service: String,
    status: String,
}

#[derive(Serialize)]
struct FullStatus {
    status: String,
    services: Vec<ServiceStatus>,
}

async fn check_service(url: &str) -> String {
    let response = reqwest::get(url).await;
    match response {
        Ok(resp) => {
            if resp.status().is_success() {
                "UP".to_string()
            } else {
                "DOWN".to_string()
            }
        }
        Err(_) => "DOWN".to_string(),
    }
}

pub async fn health() -> HttpResponse {
    let user_service_url = env::var("USER_SERVICE_URL").unwrap();
    let log_service_url = env::var("LOG_SERVICE_URL").unwrap();

    let user_service_status = check_service(&user_service_url).await;
    let log_service_status = check_service(&log_service_url).await;

    let response = FullStatus {
        status: "UP".to_string(),
        services: vec![
            ServiceStatus {
                service: "User Service".to_string(),
                status: user_service_status,
            },
            ServiceStatus {
                service: "Log Service".to_string(),
                status: log_service_status,
            },
        ],
    };

    HttpResponse::Ok().json(response)
}

pub async fn health_ready() -> HttpResponse {
    HttpResponse::Ok().body("READY")
}

pub async fn health_live() -> HttpResponse {
    HttpResponse::Ok().body("ALIVE")
}
