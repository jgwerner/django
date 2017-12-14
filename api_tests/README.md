# Writing API Tests



### Getting Started
#### Install requirements
All instructions and commands assume you are running from the root directory of app-backend.

1. Install [NodeJs](https://nodejs.org/en/).
2. Install the package dependencies:
```bash
npm install
```
#### Running the tests


1. Start app-backend
2. Verify settings in api_tests/config.js are correct
3. Start the tests: 
```bash
npm test
```


### Writing Some Tests

#### Chakram JS
The test framework we are using to test the rest api is CharkramJS. While writing tests you may want too look as some of their examples and documention which can be found below:
* [Chakram Examples](http://dareid.github.io/chakram/example/spotify/)
* [Chakram Documenation](http://dareid.github.io/chakram/jsdoc/index.html)


#### Naming scheme
Files should be named in the format ENDPOINT_test.js for example:
* me_test.js
* projects_test.js
* search_test.js

Since chakram uses mocha to run the tests, "*test*" needs to be in the file name to be automatically discovered.

Test cases should be named in the format METHOD SCENARIO should EXPECTED_RESULT for example:
* POST a valid team should create a new team
* DELETE an existing team should remove a team

#### Logging into app-backend
Most of the restful endpoints require authentication. So we need to set the authentication header before running tests:

```javascript
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
```

Then you just need to pass the options variable into the chakram method you are using:
```javascript
//Get request
chakram.get(uri, this.options);
//put with json body
chakram.put(uri, json, this.options);
//delete with no body
chakram.delete(uri, {}, this.options);
```

#### Chaining multiple request together
Some tests may require multiple request to verify an expected result, such as a put followed by a get or delete. Chakram makes use of promises to solve this problem:

```javascript
it('DELETE an existing team should remove the team', () => {
        let uri = tools.get_request_uri("me/teams/");
        return chakram.post(uri, team_json, this.options)
            .then(response => {
                expect(response).to.have.status(201);
                expect(response).to.comprise.of.json(team_json);
                uri += team_json.name + "/";
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
```

#### Make tests rerunnable when possible
Technically since the tests are run as apart of the build, we dont *need* the test to be rerunnable. But allowing the tests to be rerunnable can be very beneficial when making incremental changes in a devoper environment or while debugging the tests you are writting. Make use of the after hook to cleanup after yourself.
```javascript
	//If a test creates a team, we will cleanup by removing it.
    this.team;
    afterEach(() => {
        let uri = tools.get_request_uri("me/teams/");
        if (this.team) {
            let response = chakram.delete(uri + this.team + "/", {}, this.options)
            this.team = undefined;
            expect(response).to.have.status(204);
            return chakram.wait();
        }
    });
```