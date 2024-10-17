# APLICACIÓN EN GO CON CRUD DE USUARIOS Y AUTOMATIZACIÓN DE PRUEBAS (Taller 2 y 3)

## Integrantes

- Eric Bedoya Rendón
- Yhonatan Gómez Valencia
- Michael Aristizabal Molina
- Jacobo Sanchez Brito

## Instrucciones

### 1. Configuración del Correo Electrónico

#### 1.1. Crear un correo electrónico de su preferencia y activar la verificación en dos pasos.
#### 1.2. Modificar el código en `email.go` que se encuentra en la carpeta `/utils/`:

  ```go
     var (
         smtpHost     = "smtp.gmail.com"
         smtpPort     = 587
         fromEmail    = "" // Cambiar por el correo emisor
         password     = "" // Cambiar por la contraseña autogenerada en la verificación de dos pasos
     )
```
### 2. Construcción y Ejecución del Proyecto

  Abrir una `terminal` en la raíz del proyecto y ejecutar los siguientes comandos (asegúrese de estar en superusuario):

  Para iniciar la aplicación por primera vez, utiliza el siguiente comando:

    docker-compose up --build

  Si ya se ha ejecutado y solo deseas reanudar la aplicación, ejecuta:

    docker-compose up

### 3. Implementación y Ejecución de Pruebas
  Para las pruebas, se implementó un script. Solo necesitas navegar a la carpeta de `/test` y ejecutar:

    cd tests
    npm run test:app

### 4. Configuración de Jenkins
#### 4.1. Navegar a la carpeta donde se encuentra el Dockerfile de Jenkins:
cd /test/jenkins/
docker build -t jenkins-container .

#### 4.2. Para ejecutar Jenkins en:

   * Windows:

   
      docker run -d -v /var/run/docker.sock:/var/run/docker.sock -v jenkins_home:/var/jenkins_home -p 8081:8080 --name jenkins jenkins-container
      
   * Linux:

   
    ```docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \  
  -v jenkins_home:/var/jenkins_home \            
  -p 8081:8080 \                                 
  --name jenkins \
  jenkins-container```

#### 4.3. Acceder a la consola del contenedor:

```
  docker exec -it --user root jenkins bash
```

#### 4.4. Dentro de la consola del contenedor, ejecutar:

```
  usermod -aG docker jenkins
  sudo chmod 666 /var/run/docker.sock
```

#### 4.5. Para salir de la consola:

```
  exit
```

#### 4.6. Reiniciar el contenedor:

  ```
  docker restart jenkins
```

#### 4.7. Abrir en el navegador: 
```

  http://localhost:8081/
```

#### 4.8. Obtener la contraseña por defecto de Jenkins:

  ```
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

#### 4.9. Descargar los plugins recomendados.

#### 4.10. Despliegue en Jenkins

  Para desplegar en Jenkins, puedes hacerlo de las siguientes maneras:

* proyecto freestyle:


   - Introduce la URL del proyecto de GitHub: https://github.com/BREric/microservices
   - Selecciona terminal de sh y dentro de esa terminal, ejecuta los mismos comandos que en el primer paso (Docker Compose y npm run test).

* proyecto pipelines:

   ``` pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker-compose up --build -d'
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    sh 'npm run test:app'
                }
            }
        }
    }
} ```



### 5. Configuración del Docker Compose

Modificar las siguientes líneas dentro del docker-compose.yml:
```
services:
  mongodb_go:
    image: mongo:latest
    container_name: mongodb_container_go
    ports:
      - "27018:27017"  
    command: mongod --noauth
    volumes:
      - microtaller2_mongodb_data:/data/db
    networks:
      - microtaller_network

  api:
    build: ./app
    container_name: go_api_container
    ports:
      - "8080:8080"
    depends_on:
      - mongodb_go
    environment:
      MONGO_URI: mongodb://mongodb_go:27017/logs  
      MONGO_DB: logs
      RABBITMQ_HOST: amqp://guest:guest@rabbitmq:5672/
      RABBITMQ_QUEUE: logs_queue
      JWT_SECRET_KEY: your_secret_key
    networks:
      - microtaller_network

  mongodb_py:
    image: mongo:latest
    container_name: mongodb_container_py
    ports:
      - "27017:27017"  
    command: mongod --noauth
    volumes:
      - micro_mongodb_data_py:/data/db
    networks:
      - microtaller_network

  logs_service:
    build: ./logs_service
    container_name: python_logs_service
    ports:
      - "5000:5000"
    depends_on:
      - mongodb_py
    environment:
      MONGO_URI: mongodb://mongodb_py:27017/logs
      MONGO_DB: logs
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_QUEUE: logs_queue
      JWT_SECRET_KEY: your_secret_key
    networks:
      - microtaller_network

  rabbitmq:
    image: rabbitmq:management
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - microtaller_network

volumes:
  microtaller2_mongodb_data:
    external: false  # Cambiar a false
  micro_mongodb_data_py:
    external: false  

networks:
  microtaller_network:
    driver: bridge
```

## NOTA FINAL:

Asegúrate de que todos los servicios estén corriendo antes de realizar pruebas.
Si encuentras algún problema, revisa los logs de Docker para identificar posibles errores.

