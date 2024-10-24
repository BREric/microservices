const { Given, When, Then } = require('@cucumber/cucumber');
const request = require('supertest');
const assert = require('assert');
const Ajv = require('ajv');
const ajv = new Ajv();
require('ajv-formats')(ajv);
const apiURL = require('../support/supertestConfig');
const apiSchema = require('../schemas/apiResponsesSchema.json');

let response;
let loginData = {};
let requestTime;

// Scenario 1: Yo como usuario autenticado quiero autenticarme en el sistema
Given('soy un usuario registrado en el sistema', function () {
    requestTime = new Date();
    loginData = {
        username: 'Jhonatan',
        password: '123456'
    };
});

When('realizo una solicitud POST a login', async function () {
    response = await request(apiURL)
        .post('/login')
        .send(loginData)
        .set('Accept', 'application/json');
});

Then('obtengo un token de autenticación', function () {
    assert(response.body.token, 'No se recibió un token en la respuesta.');

    // Validar la estructura de la respuesta con JSON Schema
    const valid = ajv.validate(apiSchema.properties.LoginResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

Then('el código de estado debe ser 200', function () {
    assert.strictEqual(response.statusCode, 200);
});

Then('el servicio de logs debe contener un registro que indique un inicio de sesión exitoso', async function () {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const logResponse = await request('http://localhost:5000')
        .get('/logs')
        .query({ app_name: 'MyGoApp', log_type: 'INFO' })
        .set('Accept', 'application/json');

    assert.strictEqual(logResponse.statusCode, 200, 'La respuesta del servicio de logs no tiene el código de estado esperado.');
    const logs = logResponse.body;

    const filteredLogs = logs.filter(log => new Date(log.created_at) > requestTime);

    const logEntry = filteredLogs.find(log =>
        log.summary.includes('Solicitud POST /login') &&
        log.description.includes('Estado: 200')
    );
    assert(logEntry, `No se encontró ningún registro de log relacionado con el inicio de sesión exitoso del usuario: ${loginData.username}`);
});

// Scenario 2: Intentar iniciar sesión con credenciales incorrectas
Given('No soy un usuario registrado en el sistema', function () {
    requestTime = new Date();
    loginData = {
        username: 'wronguser',
        password: 'WrongPass'
    };
});

When('se envía la solicitud de login con credenciales incorrectas', async function () {
    response = await request(apiURL)
        .post('/login')
        .send(loginData)
        .set('Accept', 'application/json');
});

Then('obtengo un código de estado 401 indicando credenciales inválidas', function () {
    assert.strictEqual(response.statusCode, 401);

    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.ErrorResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

Then('el servicio de logs debe contener un registro que indique un intento fallido de inicio de sesión debido a credenciales inválidas', async function () {
    await new Promise(resolve => setTimeout(resolve, 2000));

    const logResponse = await request('http://localhost:5000')
        .get('/logs')
        .query({ app_name: 'MyGoApp' }) // Buscar por 'app_name' y luego filtrar más abajo
        .set('Accept', 'application/json');

    assert.strictEqual(logResponse.statusCode, 200, 'La respuesta del servicio de logs no tiene el código de estado esperado.');
    const logs = logResponse.body;

    const filteredLogs = logs.filter(log => new Date(log.created_at) > requestTime);

    const logEntry = filteredLogs.find(log =>
        log.summary.includes('Solicitud POST /login') &&
        log.description.includes('Estado: 401')
    );
    assert(logEntry, `No se encontró ningún registro de log relacionado con el intento fallido de inicio de sesión del usuario: ${loginData.username}`);
});

