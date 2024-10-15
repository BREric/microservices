# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Establecer la variable de entorno para Flask
ENV FLASK_APP=app.py

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000

# Comando para correr la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]