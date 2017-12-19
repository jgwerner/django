const chakram = require('chakram');
const util = require('util');
const config = require('./config');
const tools = require('./test_utils');
const faker = require('faker');
const expect = chakram.expect;

before(() => {
    let token = tools.login(config.username, config.password);
    this.options = {
        headers: {
            Authorization: util.format('%s %s', 'Bearer', token)
        }
    }
});

let teams_uri = tools.get_request_uri("me/teams/");

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

    it('GET should return me', () => {
        let uri = tools.get_request_uri("me");
        let response = chakram.get(uri, this.options);
        expect(response).to.have.status(200);
        expect(response).to.have.schema(me_schema);
        expect(response).to.have.json('username', config.username);
        expect(response).to.have.json('email', config.email);
        expect(response).to.have.header('content-type', 'application/json');
        return chakram.wait();
    });
});

describe('me/teams', () => {

    this.team;
    beforeEach(() => {
        this.team_json = {
            name: faker.lorem.words(1),
            description: faker.lorem.sentence(),
            website: "http://" + faker.internet.domainName(),
            location: faker.address.country()
        };
    });
    afterEach(() => {
        if (this.team) {
            let response = chakram.delete(teams_uri + this.team + "/", {}, this.options)
            this.team = undefined;
            expect(response).to.have.status(204);
            return chakram.wait();
        }
    });

    it('POST a valid team should create a new team', () => {
        return chakram.post(teams_uri, this.team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(this.team_json);
                this.team = response.body.name
                let uri = teams_uri + this.team_json.name
                return chakram.get(uri, this.options);
            })
            .then(response => {
                expect(response).to.have.status(200);
                expect(response).to.comprise.of.json(this.team_json);
            });
    });

    it('DELETE an existing team should remove the team', () => {
        let uri = teams_uri + this.team_json.name + "/";
        return chakram.post(teams_uri, this.team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(this.team_json);
                return chakram.delete(uri, {}, this.options);
            })
            .then(response => {
                expect(response).to.have.status(204);
                return chakram.get(uri, this.options);
            })
            .then(response => {
                expect(response).to.have.status(404);
            });
    });

    it('PATCH an existing team should modify a team', () => {
        let modified_team = JSON.parse(JSON.stringify(this.team_json));
        return chakram.post(teams_uri, this.team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(this.team_json);
                let uri = teams_uri + this.team_json.name + "/";
                modified_team.name = "TestTeam123"
                return chakram.patch(uri, modified_team, this.options);
            })
            .then(response => {
                expect(response).to.have.status(200);
                this.team = modified_team.name;
                expect(response).to.comprise.of.json(modified_team);
            });
    });

    it('PUT an existing team should modify a team', () => {
        let modified_team = JSON.parse(JSON.stringify(this.team_json));
        return chakram.post(teams_uri, this.team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(this.team_json);
                let uri = teams_uri + this.team_json.name + "/";
                modified_team.name = "TestTeam123"
                return chakram.put(uri, modified_team, this.options);
            })
            .then(response => {
                expect(response).to.have.status(200);
                this.team = modified_team.name;
                expect(response).to.comprise.of.json(modified_team);
            });
    });
});

describe('me/teams/{team}/groups', () => {
    this.group;
    before(() => {
        this.uri;
        this.team_json = {
            name: faker.lorem.words(1),
            description: faker.lorem.sentence(),
            website: "http://" + faker.internet.domainName(),
            location: faker.address.country()
        };
        return chakram.post(teams_uri, this.team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(this.team_json);
                this.uri = tools.get_request_uri('me/teams');
                this.uri = util.format('%s/%s/groups/', this.uri, this.team_json.name);
                this.team_json = response.body;
            })
    });

    after(() => {
        let response = chakram.delete(teams_uri + this.team_json.name + "/", {}, this.options);
        expect(response).to.have.status(204);
        return chakram.wait();
    });

    it('GET groups should return a list of groups', () => {
        let schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string"
                    },
                    "team": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    },
                    "permissions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "members": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "private": {
                        "type": "boolean"
                    },
                    "parent": {
                        "type": ["null", "string"]
                    }
                }
            }
        }
        return chakram.get(this.uri, this.options)
            .then(response => {
                expect(response).to.have.status(200);
                expect(response).to.have.schema(schema);
            });
    });

    it('POST a group should return a valid group', () => {
        let group_parent;
        let group = {
            name: faker.lorem.words(1),
            permissions: [],
            private: true,
            parent: ""
        }
        return chakram.get(this.uri, this.options)
            .then(response => {
                expect(response).to.have.status(200);
                group_parent = response.body[0].name;
                group.parent = response.body[0].id;
                return chakram.post(this.uri, group, this.options);
            })
            .then(response => {
                group.parent = group_parent;
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(group);
            });
    });
});
