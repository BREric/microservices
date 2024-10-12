# APLICACION EN GO CON CRUD DE USUARIOS Y AUTOMATIZACION DE PRUEBAS (Taller 2 y 3)

## Integrantes:

- Eric Bedoya Rendón
- Yhonatan Gómez Valencia
- Michael Aristizabal Molina
- Jacobo Sanchez Brito


## Instrucciones
1. Crear un correo electronico de su preferencia y activar la verificacion en dos pasos
   ### Modificar el codigo de email.go que se encuentra en la carpeta de /utils/
       -var (
       smtpHost     = "smtp.gmail.com"
       smtpPort     = 587
       fromEmail    = "" 
       password     = "" 
       )
     **cambiar las variables fromEmail por el correo emisor del mensaje, cambiar password por la contrasena autogenerada en la verificaccion de dos pasos.**

2. Abrir una terminal en la raiz del proyecto y ejecutar los siguientes comandos (Asegurese de estar en superusuario):
   - Montar la imagen del proyecto construyendo el dockerfile `docker build -t go_api_container .`.
   - Hacer cd a logs_services y ejecutar `docker build -t python_logs_service .`
   - Posteriormente, construir el docker compose con `docker-compose build`.
   - Por ultimo, levantar el contenedor `docker-compose up`.
  

3. Implementacion y ejecucion de pruebas :
- Ejecuta las pruebas y genera un reporte en un html estatico detallado `npx mocha api.test.js --reporter mochawesome`
- Ejecuta pruebas de todas las apis con feature y steps `npx cucumber-js .\tests\features\ --require tests/step_definitions`


Navegar a la carpeta donde se encuentra el dockerfile de jenkins /jenkins/
docker build -t jenkins-container .

para windows> docker run -d -v /var/run/docker.sock:/var/run/docker.sock -v jenkins_home:/var/jenkins_home -p 8081:8080 --name jenkins jenkins-container

Para linux> docker run -d \
  -v /var/run/docker.sock:/var/run/docker.sock \  
  -v jenkins_home:/var/jenkins_home \            
  -p 8081:8080 \                                 
  --name jenkins \
  jenkins-container
  
ejecutar para acceder a la consola de el contenedor
docker exec -it --user root jenkins bash

una vez dentro de la consola del contenedor ejecutar
usermod -aG docker jenkins
sudo chmod 666 /var/run/docker.sock
npm install -g cucumber

para salir de la consola
exit 

por ultimo reinciar el contenedor
docker restart jenkins

abrir el localhost http://localhost:8081/
EJecutar para obtener la contrasena por defecto del jenkins docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

Descargar los plugins recomendados

habilitar una bash terminal en el job y poner las siguientes lineas de codigo>



docker exec -it mongodb_container mongosh
use logs
show collections  // Para ver las colecciones
db.logs.find().pretty()  // Para ver los documentos en la colección 'logs'


docker build --tag jenkins-container --pull .
docker-compose up -d --no-recreate --build

sleep 10

npm run test
