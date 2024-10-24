use actix_web::{web, App, HttpResponse, HttpServer};
use serde::Serialize;
use std::env;
use std::time::{SystemTime, UNIX_EPOCH};
use mysql::*;
use mysql::prelude::*;
use mysql::OptsBuilder;

mod handlers;
mod utils;

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    checks: Vec<HealthCheck>,
}

#[derive(Serialize)]
struct HealthCheck {
    name: String,
    status: String,
    data: HealthCheckData,
}

#[derive(Serialize)]
struct HealthCheckData {
    from: String,
    status: String,
}

async fn health_check() -> HttpResponse {
    let uptime = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    let time_up = uptime.as_secs();

    let health_response = HealthResponse {
        status: "UP".to_string(),
        checks: vec![
            HealthCheck {
                name: "Readiness check".to_string(),
                status: "UP".to_string(),
                data: HealthCheckData {
                    from: format!("{}", time_up),
                    status: "READY".to_string(),
                },
            },
            HealthCheck {
                name: "Liveness check".to_string(),
                status: "UP".to_string(),
                data: HealthCheckData {
                    from: format!("{}", time_up),
                    status: "ALIVE".to_string(),
                },
            },
        ],
    };

    HttpResponse::Ok().json(health_response)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    let user_service_url = env::var("USER_SERVICE_URL").expect("USER_SERVICE_URL must be set");
    let log_service_url = env::var("LOG_SERVICE_URL").expect("LOG_SERVICE_URL must be set");

    // Conexión MySQL usando la URL completa de la variable de entorno
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    // Usa la URL completa en lugar de descomponer manualmente los parámetros
    let opts = Opts::from_url(&db_url).expect("Error parsing DATABASE_URL");

    let pool = Pool::new(opts).unwrap();
    let _conn = pool.get_conn().unwrap(); // Conexión a MySQL

    println!("User Service URL: {}", user_service_url);
    println!("Log Service URL: {}", log_service_url);

    HttpServer::new(|| {
        App::new()
            .route("/health", web::get().to(handlers::health))
            .route("/health/ready", web::get().to(handlers::health_ready))
            .route("/health/live", web::get().to(handlers::health_live))
    })
    .bind(("0.0.0.0", 8081))?
    .run()
    .await
}
