const chakram = require('chakram')
const util = require('util')
const config = require('./config')
const tools = require('./test_utils')
const faker = require('faker')
const expect = chakram.expect

before(async () => {
  const token = await tools.login(config.username, config.password)
  this.options = {
    headers: {
      Authorization: util.format('%s %s', 'Bearer', token),
    },
  }
})

describe('users/profiles/', () => {
  const profile_uri = tools.get_request_uri('users/profiles/')
  const user_schema = {
    type: 'array',
    items: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
        },
        username: {
          type: 'string',
        },
        email: {
          type: 'string',
        },
        first_name: {
          type: 'string',
        },
        last_name: {
          type: 'string',
        },
        profile: {
          type: 'object',
          properties: {
            bio: {
              type: ['null', 'string'],
            },
            url: {
              type: ['null', 'string'],
            },
            location: {
              type: ['null', 'string'],
            },
            company: {
              type: ['null', 'string'],
            },
            timezone: {
              type: ['null', 'string'],
            },
            avatar: {
              type: ['null', 'string'],
            },
          },
        },
      },
    },
  }

  beforeEach(() => {
    this.new_user = {
      username: faker.internet.userName(),
      email: faker.internet.exampleEmail(),
      first_name: faker.name.firstName(),
      last_name: faker.name.lastName(),
      password: faker.internet.password(),
      profile: {
        bio: faker.lorem.sentence(),
        location: faker.address.country(),
        company: faker.company.companyName(),
      },
    }
  })

  it('GET all user profiles should return a list of profiles', async () => {
    const response = await chakram.get(profile_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(user_schema)
  })

  it('DELETE deleting a new user should remove the user', async () => {
    let user_uri
    const response = await chakram.post(profile_uri, this.new_user, this.options)
    let expect_json = JSON.parse(JSON.stringify(this.new_user))
    delete expect_json.password
    expect(response).to.have.status(201)
    expect(response).to.comprise.of.json(expect_json)
    user_uri = profile_uri + response.body.id + '/'

    const del_response = await chakram.delete(user_uri, {}, this.options)
    expect(del_response).to.have.status(204)

    const get_response = await chakram.get(user_uri, this.options)
    expect(get_response).to.have.status(404)
  })

  it('PATCH changing a users email should update the email', async () => {
    let user_uri
    let modified_user = JSON.parse(JSON.stringify(this.new_user))
    modified_user.profile.bio = faker.lorem.sentence()
    delete modified_user.username
    delete modified_user.password
    const response = await chakram.post(profile_uri, this.new_user, this.options)
    expect(response).to.have.status(201)
    user_uri = profile_uri + response.body.id + '/'

    const patch_response = await chakram.patch(user_uri, modified_user, this.options)
    expect(patch_response).to.have.status(200)

    const get_response = await chakram.get(user_uri, this.options)
    expect(get_response).comprise.of.json(modified_user)
  })
})

describe('users/{user_id}/emails/', async () => {
  let me
  let email_uri
  before(async () => {
    const me_uri = tools.get_request_uri('me/')

    const response = await chakram.get(me_uri, this.options)
    expect(response).to.have.status(200)
    me = response.body
    email_uri = tools.get_request_uri(util.format('users/%s/emails/', me.id))
  })

  beforeEach(() => {
    this.email = {
      address: faker.internet.exampleEmail(),
      public: true,
      unsubscribed: true,
    }
  })

  afterEach(async () => {
    if (this.delete_email) {
      const response = await chakram.delete(email_uri + this.delete_email + '/', {}, this.options)
      expect(response).to.have.status(204)
      this.delete_email = undefined
    }
  })

  it('POST a user email should return the email', async () => {
    const response = await chakram.post(email_uri, this.email, this.options)
    expect(response).to.have.status(201)
    this.delete_email = response.body.id

    const get_response = await chakram.get(email_uri + response.body.id + '/', this.options)
    expect(get_response).to.have.status(200)
    expect(get_response).comprise.of.json(this.email)
  })

  it('PUT changing the address should return the new address', async () => {
    let modified_email = JSON.parse(JSON.stringify(this.email))
    modified_email.address = faker.internet.exampleEmail()
    const response = await chakram.post(email_uri, this.email, this.options)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)
    this.delete_email = response.body.id
    const uri = email_uri + response.body.id + '/'

    const put_response = await chakram.put(uri, modified_email, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).comprise.of.json(modified_email)
  })

  it('PATCH changing the address should return the new address', async () => {
    let modified_email = JSON.parse(JSON.stringify(this.email))
    modified_email.address = faker.internet.exampleEmail()
    const response = await chakram.post(email_uri, this.email, this.options)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)
    this.delete_email = response.body.id
    const uri = email_uri + response.body.id + '/'

    const put_response = await chakram.patch(uri, modified_email, this.options)
    expect(put_response).to.have.status(200)
    expect(put_response).comprise.of.json(modified_email)
  })

  it('DELETE deleting the email should remove the email', async () => {
    const response = await chakram.post(email_uri, this.email, this.options)
    expect(response).to.have.status(201)
    expect(response).comprise.of.json(this.email)

    const del_response = await chakram.delete(email_uri + response.body.id + '/', {}, this.options)
    expect(del_response).to.have.status(204)
  })
})

describe('users/{user_id}/api-key/', () => {
  let schema = {
    type: 'object',
    properties: {
      token: {
        type: 'string',
      },
    },
  }
  let api_key_uri
  before(async () => {
    const me_uri = tools.get_request_uri('me/')
    const response = await chakram.get(me_uri, this.options)
    expect(response).to.have.status(200)
    me = response.body
    api_key_uri = tools.get_request_uri(util.format('users/%s/api-key/', me.id))
  })

  it('GET user api key should retrieve a valid api key', async () => {
    const response = await chakram.get(api_key_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
  })

  it.skip('POST refresh key should retrieve a new valid api key | endpoint missing', async () => {
    const refresh_uri = api_key_uri + 'reset/'
    const response = await chakram.post(refresh_uri, {}, this.options)
    expect(response).to.have.status(201)
    expect(response).to.have.schema(schema)
  })
})

describe('users/{user_id}/ssh-key', () => {
  let ssh_key_uri
  const ssh_schema = {
    type: 'object',
    key: {
      type: 'string',
    },
  }
  before(async () => {
    const me_uri = tools.get_request_uri('me/')
    const response = await chakram.get(me_uri, this.options)
    expect(response).to.have.status(200)
    me = response.body
    ssh_key_uri = tools.get_request_uri(util.format('users/%s/ssh-key/', me.id))
  })

  it('GET my ssh key should provide a valid ssh key', async () => {
    const response = await chakram.get(ssh_key_uri, this.options)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(ssh_schema)
  })
})
