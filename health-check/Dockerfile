# Fase de construcción (builder)
FROM rust:1.72 as builder

# Establecer el directorio de trabajo
WORKDIR /usr/src/app

# Copiar todos los archivos del proyecto al contenedor
COPY . .

# Compilar la aplicación en modo release
RUN cargo build --release

# Fase de ejecución (runtime stage)
FROM debian:bookworm-slim

# Establecer el directorio de trabajo para la fase de ejecución
WORKDIR /usr/local/bin

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar el binario compilado desde la fase builder
COPY --from=builder /usr/src/app/target/release/health-check /usr/local/bin/health-check

# Ejecutar un sleep de 15 segundos antes de iniciar el servicio
CMD ["sh", "-c", "sleep 15 && ./health-check"]
