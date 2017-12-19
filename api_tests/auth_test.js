const chakram = require('chakram');
const util = require('util');
const config = require('./config');
const tools = require('./test_utils');
const faker = require('faker');
const expect = chakram.expect;

let auth_uri = tools.get_request_uri('auth/jwt-token-auth/', true);

describe('auth/jwt-token-auth/', () => {

    it('POST valid credentials should provide an authorization token', () => {
        let response = chakram.post(auth_uri, { username: config.username, password: config.password });
        expect(response).to.have.status(201);
        expect(response).to.have.schema({
            "type": "object",
            properties: {
                token: {
                    type: "string"
                }
            }
        });
        return chakram.wait();
    });

    it('POST invalid credentials should return 400', () => {
        let response = chakram.post(auth_uri, { username: config.username, password: "Wrong Password" });
        expect(response).to.have.status(400);
        return chakram.wait();
    });
});

describe('auth/jwt-token-refresh/', () => {
    let refresh_uri = tools.get_request_uri('auth/jwt-token-refresh/', true);

    it('POST valid authentication token should return a valid refreshed token', () => {
        return chakram.post(auth_uri, { username: config.username, password: config.password })
            .then(response => {
                expect(response).to.have.status(201);
                return chakram.post(refresh_uri, response.body);
            })
            .then(response => {
                expect(response).to.have.status(201);
                return expect(response).to.have.schema({
                    "type": "object",
                    properties: {
                        token: {
                            type: "string"
                        }
                    }
                });
            });
    });

    it('POST invalid authentication token should return 400', () => {
        let response = chakram.post(refresh_uri, { token: "NotARealToken" });
        expect(response).to.have.status(400);
        return chakram.wait();
    });
});

describe('auth/jwt-token-verify/', () => {
    let verify_uri = tools.get_request_uri('auth/jwt-token-verify/', true);

    it('POST valid authentication token should return return the verified token', () => {
        return chakram.post(auth_uri, { username: config.username, password: config.password })
            .then(response => {
                expect(response).to.have.status(201);
                return chakram.post(verify_uri, response.body);
            })
            .then(response => {
                expect(response).to.have.status(201);
                return expect(response).to.have.schema({
                    "type": "object",
                    properties: {
                        token: {
                            type: "string"
                        }
                    }
                });
            });
    });

    it('POST invalid authentication token should return 400', () => {
        let response = chakram.post(verify_uri, { token: "NotARealToken" });
        expect(response).to.have.status(400);
        return chakram.wait();
    });
});

describe('auth/temp-token-auth/', () => {
    let temp_token = tools.get_request_uri('auth/temp-token-auth/', true);

    it('GET valid login should return a valid temp token', () => {
        return chakram.post(auth_uri, { username: config.username, password: config.password })
            .then(response => {
                expect(response).to.have.status(201);
                let options = {
                    headers: {
                        Authorization: util.format('%s %s', 'Bearer', response.body.token)
                    }
                }
                return chakram.get(temp_token, options);
            })
            .then(response => {
                expect(response).to.have.status(200);
                return expect(response).to.have.schema({
                    "type": "object",
                    properties: {
                        token: {
                            type: "string"
                        }
                    }
                });
            });
    });
});

describe('auth/register/', () => {
    let new_user = {
        username: faker.internet.userName(),
        email: faker.internet.email(),
        first_name: faker.name.firstName(),
        last_name: faker.name.lastName(),
        password: faker.internet.password(),
        profile: {
            bio: faker.lorem.sentence(),
            location: faker.address.country(),
            company: faker.company.companyName()
        }
    }
    let register_uri = tools.get_request_uri('auth/register/', true);    
    it('POST valid username should return a valid user object', () => {
        return chakram.post(register_uri, new_user)
            .then(response => {
                let expect_json = JSON.parse(JSON.stringify(new_user));
                delete expect_json.password;
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(expect_json);
            });
    });
});



