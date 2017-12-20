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

describe('actions', () => {
  let schema = {
    type: 'array',
    items: {
      type: 'object',
      properties: {
        id: {
          type: 'string',
        },
        resource_uri: {
          type: 'string',
        },
        payload: {
          type: 'object',
        },
        action: {
          type: 'string',
        },
        method: {
          type: 'string',
        },
        user: {
          type: ['null', 'string'],
        },
        user_agent: {
          type: 'string',
        },
        start_date: {
          type: 'string',
        },
        end_date: {
          type: ['null', 'string'],
        },
        state: {
          type: 'string',
        },
        ip: {
          type: 'string',
        },
        object: {
          type: 'string',
        },
        is_user_action: {
          type: 'boolean',
        },
        can_be_cancelled: {
          type: 'boolean',
        },
        can_be_retried: {
          type: 'boolean',
        },
        path: {
          type: 'string',
        },
      },
    },
  }

  it.skip('GET 5 actions should return 5 actions | DISABLED', async () => {
    let uri = tools.get_request_uri('actions/')
    let limit = 5
    uri += '?limit=' + limit
    const response = await chakram.get(uri, this.options)
    expect(response).to.have.status(200)
    expect(response.body.length).to.equal(limit)
    expect(response).to.have.schema(schema)
  })
})
