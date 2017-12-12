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

describe('me', () => {

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

    it('GET me should return me', () => {
        let uri = tools.get_request_uri("me");
        let response = chakram.get(uri, this.options);
        expect(response).to.have.status(200);
        expect(response).to.have.schema(me_schema);
        expect(response).to.have.json('username', config.username);
        expect(response).to.have.json('email', config.email);
        expect(response).to.have.header('content-type', 'application/json');
        return chakram.wait();
    });

    it('POST me/teams should create a new team', () => {
        let uri = tools.get_request_uri("me/teams/");
        let team_json = {
            name: "TestTeam",
            description: "TestTeam",
            website: "http://mywebsite.com",
            location: "here"
        };
        return chakram.post(uri, team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(team_json);
                uri += team_json.name
                return chakram.get(uri, this.options);
            })
            .then(response => {
                expect(response).to.have.status(200);
                expect(response).to.comprise.of.json(team_json);
            });
    });
})
