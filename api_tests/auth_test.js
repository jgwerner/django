const chakram = require('chakram')
const util = require('util')
const config = require('./config')
const tools = require('./test_utils')
const generator = require('./generator')
const expect = chakram.expect

const auth_uri = tools.get_request_uri('auth/jwt-token-auth/', true)
const schema = tools.get_schema('auth', 'auth/')
const valid_login = {
  username: config.username,
  password: config.password,
}
const invalid_login = {
  username: config.username,
  password: 'Wrong Password',
}

describe('auth/jwt-token-auth/', () => {
  it('POST valid credentials should provide an authorization token', async () => {
    const response = await chakram.post(auth_uri, valid_login)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(schema)
  })

  it('POST invalid credentials should return 400', async () => {
    const response = await chakram.post(auth_uri, invalid_login)
    expect(response).to.have.status(400)
  })
})

describe('auth/jwt-token-refresh/', () => {
  const refresh_uri = tools.get_request_uri('auth/jwt-token-refresh/', true)

  it('POST valid authentication token should return a valid refreshed token', async () => {
    const response = await chakram.post(auth_uri, valid_login)
    expect(response).to.have.status(201)

    const post_response = await chakram.post(refresh_uri, response.body)
    expect(post_response).to.have.status(201)
    expect(post_response).to.have.schema(schema)
  })

  it('POST invalid authentication token should return 400', async () => {
    const response = await chakram.post(refresh_uri, { token: 'NotARealToken' })
    expect(response).to.have.status(400)
  })
})

describe('auth/jwt-token-verify/', () => {
  const verify_uri = tools.get_request_uri('auth/jwt-token-verify/', true)

  it('POST valid authentication token should return return the verified token', async () => {
    const response = await chakram.post(auth_uri, valid_login)
    expect(response).to.have.status(201)

    const post_response = await chakram.post(verify_uri, response.body)
    expect(post_response).to.have.status(201)
    expect(post_response).to.have.schema(schema)
  })

  it('POST invalid authentication token should return 400', async () => {
    let response = await chakram.post(verify_uri, { token: 'NotARealToken' })
    expect(response).to.have.status(400)
  })
})

describe('auth/temp-token-auth/', () => {
  const temp_token = tools.get_request_uri('auth/temp-token-auth/', true)

  it('GET valid login should return a valid temp token', async () => {
    const response = await chakram.post(auth_uri, valid_login)
    expect(response).to.have.status(201)
    const options = {
      headers: {
        Authorization: util.format('%s %s', 'Bearer', response.body.token),
      },
    }

    const get_response = await chakram.get(temp_token, options)
    expect(get_response).to.have.status(200)
    expect(get_response).to.have.schema(schema)
  })
})

describe('auth/register/', () => {
  const new_user = generator.user()
  const register_uri = tools.get_request_uri('auth/register/', true)

  it('POST valid username should return a valid user object', async () => {
    const response = await chakram.post(register_uri, new_user)
    let expect_json = JSON.parse(JSON.stringify(new_user))
    delete expect_json.password
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(expect_json)
  })
})
