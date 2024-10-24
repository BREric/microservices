const { Given, When, Then } = require('@cucumber/cucumber');
const request = require('supertest');
const assert = require('assert');
const Ajv = require('ajv');
const ajv = new Ajv();
require('ajv-formats')(ajv);
const apiURL = require('../support/supertestConfig');
const apiSchema = require('../schemas/apiResponsesSchema.json');

let response;
let token;
let userId;

// Scenario 1: Obtener detalles del usuario
Given('soy un usuario autenticado', async function () {
    // Realizamos login para obtener el token y el ID del usuario autenticado
    const loginResponse = await request(apiURL)
        .post('/login')
        .send({
            username: 'Jhonatan',
            password: '123456'
        });

    assert.strictEqual(loginResponse.statusCode, 200);
    token = loginResponse.body.token; // Guardamos el token de autenticación
    userId = loginResponse.body.userId;
});

When('hago una solicitud GET a users seguido de mi id', async function () {
    // Para verificar que userId es correcto
    response = await request(apiURL)
        .get(`/users/${userId}`) // Usamos el ID del usuario autenticado
        .set('Authorization', `Bearer ${token}`)
        .set('Accept', 'application/json');
});

Then('obtengo los datos de mi usuario', function () {

    assert(response.body.Username, 'No se recibieron los detalles del usuario en la respuesta.');

    // Validar la estructura de la respuesta con JSON Schema
    const valid = ajv.validate(apiSchema.properties.GetUserByIDResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});


Then('obtengo un código de estado 200 al obtener los detalles del usuario', function () {
    assert.strictEqual(response.statusCode, 200);
});

// Scenario 2: Intentar obtener detalles de otro usuario
When('realizo una solicitud GET a users seguido de un id de usuario diferente al mío', async function () {
    // Usamos un ID diferente al del usuario autenticado para este escenario
    response = await request(apiURL)
        .get(`/users/66feb4f4be9088fa139fa679`)
        .set('Authorization', `Bearer ${token}`);
});

Then('obtengo un código de estado 404 indicando que no tengo permiso para acceder a la información de otro usuario', function () {
    assert.strictEqual(response.statusCode, 404);


    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.ErrorResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

