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

Since chakram uses mocha to run the tests, "_test_" needs to be in the file name to be automatically discovered.

Test cases should be named in the format METHOD SCENARIO should EXPECTED_RESULT for example:

* POST a valid team should create a new team
* DELETE an existing team should remove a team

#### Logging into app-backend

Most of the restful endpoints require authentication. So we need to set the authentication header before running tests:

```javascript
const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const expect = chakram.expect

before(async () => {
  const token = await tools.login(config.username, config.password)
  this.options = {
    headers: {
      Authorization: util.format('%s %s', 'Bearer', token),
    },
  }
})
```

Then you just need to pass the options variable into the chakram method you are using:

```javascript
//Get request
chakram.get(uri, this.options)
//put with json body
chakram.put(uri, json, this.options)
//delete with no body
chakram.delete(uri, {}, this.options)
```

#### async/await

Javascript is asynchronous by default so in order to handle asynchronous web request we need to make use of async functions and awaiting api responses. See the example below:

```javascript
it('PATCH a project should replace the project', async () => {
  // Arrange
  const new_proj = generator.project()
  const mod_proj = generator.project()
  const post_response = await chakram.post(proj_uri, new_proj, this.options)
  expect(post_response).to.have.status(201)
  expect(post_response).to.comprise.of.json(new_proj)
  const project_uri = proj_uri + post_response.body.id + '/'
  // Act
  const patch_response = await chakram.patch(project_uri, mod_proj, this.options)
  // Assert
  expect(patch_response).to.have.status(200)
  expect(patch_response).to.comprise.of.json(mod_proj)
})
```

#### Make tests rerunnable when possible

Technically since the tests are run as apart of the build, we dont _need_ the test to be rerunnable. But allowing the tests to be rerunnable can be very beneficial when making incremental changes in a devoper environment or while debugging the tests you are writting. One way of acheiving this is using the after hooks to cleanup after a test is run:

```javascript
//If a test creates a team, we will cleanup by removing it.
afterEach(() => {
  let uri = tools.get_request_uri('me/teams/')
  if (this.team) {
    let response = chakram.delete(uri + this.team + '/', {}, this.options)
    this.team = undefined
    expect(response).to.have.status(204)
    return chakram.wait()
  }
})
```

Another option is to create a generator for the data you are posting and ensure that it will be unique:

```javascript
project() {
    return {
      name: faker.lorem.words(1) + faker.random.number(9999999),
      description: faker.lorem.sentence(),
      private: true,
      copying_enabled: true,
    }
}
```
