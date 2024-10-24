const { Given, When, Then, After, Before } = require('@cucumber/cucumber');
const request = require('supertest');
const assert = require('assert');
const { faker } = require('@faker-js/faker');
const Ajv = require('ajv');
const ajv = new Ajv();
require('ajv-formats')(ajv);
const apiURL = require('../support/supertestConfig');
const apiSchema = require('../schemas/apiResponsesSchema.json');

let response;


function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Step 1: Crear un nuevo usuario con datos válidos
Given('Tengo un nombre de usuario, email y contraseña válidos', function () {
    this.requestTime = new Date();

    this.userData = {
        username: faker.internet.userName(),
        email: faker.internet.email(),
        password: 'password123'
    };
});

When('invoco el servicio de creación de usuario con los datos', async function () {
    response = await request(apiURL)
        .post('/users')
        .send(this.userData);
    this.createdUserId = response.body.id;
});

Then('obtengo un código de estado 201', function () {
    assert.strictEqual(response.statusCode, 201);

    // Validar la estructura de la respuesta con JSON Schema
    const valid = ajv.validate(apiSchema.properties.CreateUserResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta no coincide con el esquema JSON');
    if (!valid) {
        console.log(ajv.errors);
    }
});

Then('el servicio de logs debe contener un registro que indique la creación del usuario', async function () {
    await delay(2000); // Agregar un retraso de 2 segundos

    const logResponse = await request('http://localhost:5000')
        .get('/logs')
        .query({ app_name: 'MyGoApp', log_type: 'INFO' })
        .set('Accept', 'application/json');

    assert.strictEqual(logResponse.statusCode, 200, 'La respuesta del servicio de logs no tiene el código de estado esperado.');
    const logs = logResponse.body;

    // Filtrar logs por tiempo, con margen de 5 segundos hacia atrás
    const filteredLogs = logs.filter(log => new Date(log.created_at) > new Date(this.requestTime.getTime() - 5000));

    const logEntry = filteredLogs.find(log =>
        log.summary.includes('Solicitud POST /users') &&
        log.description.includes('Estado: 201')
    );

    assert(logEntry, `No se encontró ningún registro de log relacionado con la creación del usuario: ${this.userData.username}`);
});



// Step 2: Intentar crear un usuario con nombre de usuario ya registrado
Given('Tengo un nombre de usuario ya está registrado', async function () {
    this.requestTime = new Date();
    this.userData = {
        username: 'existinguser',
        email: faker.internet.email(),
        password: faker.internet.password()
    };
});

When('invoco el servicio de creación de usuario con el nombre de usuario', async function () {
    response = await request(apiURL)
        .post('/users')
        .send(this.userData);
});

Then('obtengo un código de estado 409 indicando conflicto', function () {
    assert.strictEqual(response.statusCode, 409);
});

Then('un mensaje que indique que el nombre de usuario ya está en uso', function () {
    assert(response.body.message.includes('Username already in use'));
    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.ErrorResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log(ajv.errors);
    }
});

Then('el servicio de logs debe contener un registro que indique un intento fallido de creación debido a un nombre de usuario ya registrado', async function () {
    await delay(2000); // Agregar un retraso de 2 segundos

    const logResponse = await request('http://localhost:5000')
        .get('/logs')
        .query({ app_name: 'MyGoApp', log_type: 'INFO' })
        .set('Accept', 'application/json');

    assert.strictEqual(logResponse.statusCode, 200, 'La respuesta del servicio de logs no tiene el código de estado esperado.');
    const logs = logResponse.body;

    // Filtrar logs por tiempo, con margen de 5 segundos hacia atrás
    const filteredLogs = logs.filter(log => new Date(log.created_at) > new Date(this.requestTime.getTime() - 5000));

    const logEntry = filteredLogs.find(log =>
        log.summary.includes('Solicitud POST /users') &&
        log.description.includes('Estado: 409')
    );

    assert(logEntry, `No se encontró ningún registro de log relacionado con el intento fallido de creación del usuario: ${this.userData.username}`);
});

// Step 3: Intentar crear un usuario sin proporcionar un nombre de usuario
Given('No ingreso un nombre de usuario', function () {
    this.requestTime = new Date();
    this.userData = {
        username: '',  // Nombre de usuario vacío para esta prueba
        email: 'noUsername@example.com',
        password: 'password123'
    };
});

When('invoco el servicio de creación de usuario', async function () {
    response = await request(apiURL)
        .post('/users')
        .send(this.userData);
});

Then('obtengo un código de estado 400 indicando error en la solicitud', function () {
    assert.strictEqual(response.statusCode, 400);

    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.ErrorResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

Then('el servicio de logs debe contener un registro que indique un intento fallido de creación debido a datos incompletos', async function () {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const logResponse = await request('http://localhost:5000')
        .get('/logs')
        .query({ app_name: 'MyGoApp', log_type: 'INFO' }) // Cambiar si es necesario
        .set('Accept', 'application/json');

    assert.strictEqual(logResponse.statusCode, 200, 'La respuesta del servicio de logs no tiene el código de estado esperado.');
    const logs = logResponse.body;

    const filteredLogs = logs.filter(log => new Date(log.created_at) > this.requestTime);

    const logEntry = filteredLogs.find(log =>
        log.summary.includes('Solicitud POST /users') &&
        log.description.includes('Estado: 400')
    );
    assert(logEntry, 'No se encontró ningún registro de log relacionado con el intento fallido de creación debido a datos incompletos');
});
