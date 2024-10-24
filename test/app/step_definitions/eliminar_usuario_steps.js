const { Given, When, Then, BeforeAll } = require('@cucumber/cucumber');
const request = require('supertest');
const assert = require('assert');
const { faker } = require('@faker-js/faker');
const Ajv = require('ajv');
const ajv = new Ajv();
require('ajv-formats')(ajv);
const apiURL = require('../support/supertestConfig');
const apiSchema = require('../schemas/apiResponsesSchema.json');

let response;
let token;
let userId;
let tempUserId;  // Para almacenar el ID de la cuenta temporal que crearemos
let tempUsername; // Para almacenar el nombre de usuario temporal creado

BeforeAll(async function () {
    // Crear un nuevo usuario para usarlo en todos los tests
    tempUsername = faker.internet.userName();
    const userCreationResponse = await request(apiURL)
        .post('/users')
        .send({
            username: tempUsername,
            email: faker.internet.email(),
            password: 'password123'
        });

    assert.strictEqual(userCreationResponse.statusCode, 201, 'No se pudo crear el usuario');
    tempUserId = userCreationResponse.body.id;  // Guardamos el ID del nuevo usuario para eliminarlo luego
});

// Scenario 1: Eliminar cuenta sin autenticarse
Given('Soy un usuario no autenticado para eliminar mi cuenta', function () {
    token = null;  // Simulamos un usuario no autenticado
});

When('invoco el servicio de eliminación de mi cuenta sin autenticar', async function () {
    response = await request(apiURL)
        .delete(`/users/${tempUserId}`)
        .set('Accept', 'application/json');
});

Then('obtengo un código de estado 401 al intentar eliminar mi cuenta sin autenticar', function () {
    assert.strictEqual(response.statusCode, 401, `Expected status code 401 but got ${response.statusCode}`);

    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.UnauthorizedResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

// Scenario 2: Eliminar una cuenta que no es la del usuario autenticado
Given('Soy un usuario autenticado para eliminar otra cuenta', async function () {
    // Realizamos login con el usuario creado en el Before
    const loginResponse = await request(apiURL)
        .post('/login')
        .send({
            username: tempUsername,  // Usamos el nombre de usuario creado en el Before
            password: 'password123'
        });

    assert.strictEqual(loginResponse.statusCode, 200, `Expected status code 200 but got ${loginResponse.statusCode}`);
    token = loginResponse.body.token;
    userId = '66feb4f4be9088fa139fa679';  // ID de otro usuario que intentaremos eliminar
});

When('realizo la solicitud de eliminación de una cuenta diferente', async function () {
    response = await request(apiURL)
        .delete(`/users/${userId}`)  // Intento de eliminar otra cuenta
        .set('Authorization', `Bearer ${token}`)
        .set('Accept', 'application/json');
});

Then('obtengo un código de estado 404 al intentar eliminar una cuenta diferente', function () {
    assert.strictEqual(response.statusCode, 404, `Expected status code 403 but got ${response.statusCode}`);

    // Validar la estructura de la respuesta de error con JSON Schema
    const valid = ajv.validate(apiSchema.properties.ErrorResponse, response.body);
    assert.strictEqual(valid, true, 'La respuesta de error no coincide con el esquema JSON');
    if (!valid) {
        console.log('Errores de validación:', ajv.errors);
    }
});

// Scenario 3: Eliminar la propia cuenta
Given('Soy un usuario autenticado para eliminar mi cuenta', async function () {
    // Realizamos login con el usuario creado en el Before
    const loginResponse = await request(apiURL)
        .post('/login')
        .send({
            username: tempUsername,  // Usamos el nombre de usuario creado en el Before
            password: 'password123'
        });

    assert.strictEqual(loginResponse.statusCode, 200, `Expected status code 200 but got ${loginResponse.statusCode}`);
    token = loginResponse.body.token;  // Guardamos el token de autenticación
});

When('invoco el servicio de eliminación de mi cuenta', async function () {
    response = await request(apiURL)
        .delete(`/users/${tempUserId}`)  // Eliminamos la cuenta temporal creada
        .set('Authorization', `Bearer ${token}`)
        .set('Accept', 'application/json');
});

Then('obtengo un código de estado 204 que me indica que fue exitosa', function () {
    assert.strictEqual(response.statusCode, 204, `Expected status code 204 but got ${response.statusCode}`);

    // Validar si la respuesta es realmente null o un objeto vacío
    if (response.body === null || Object.keys(response.body).length === 0) {
        assert(true, 'La respuesta es válida y no contiene contenido, como se esperaba para un 204.');
    } else {
        assert.fail('La respuesta contiene datos inesperados.');
    }
});



