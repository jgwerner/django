const chakram = require('chakram');
const util = require('util');
const config = require('./config');
const tools = require('./test_utils')
const expect = chakram.expect;

before(() => {
    let token = tools.login(config.username, config.password);
    this.options = {
        headers: {
            Authorization: util.format('%s %s', 'Bearer', token)
        }
    }
});

describe('Verify Login', () => {

    const me_schema = {
        "type": "object",
        "properties": {
            "id": {
                "type": "string"
            },
            "username": {
                "type": "string"
            },
            "email": {
                "type": "string"
            },
            "first_name": {
                "type": "string"
            },
            "last_name": {
                "type": "string"
            }
        }
    }

    it('I should be logged in', () => {
        let uri = tools.get_request_uri("me");
        let response = chakram.get(uri, this.options);
        expect(response).to.have.status(200);
        expect(response).to.have.schema(me_schema);
        expect(response).to.have.json('username', config.username);
        expect(response).to.have.json('email', config.email);
        expect(response).to.have.header('content-type', 'application/json');
        return chakram.wait();
    });
})
