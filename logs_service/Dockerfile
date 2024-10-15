# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn
RUN pip install gunicorn

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000

# Comando para correr la aplicación con Gunicorn, usando un solo worker con hilos y configuración adicional
CMD ["gunicorn", "-c", "app/gunicorn.conf.py", "--bind", "0.0.0.0:5000", "main:app", "--workers=1", "--threads=3"]