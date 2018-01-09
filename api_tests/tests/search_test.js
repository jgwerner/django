const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const expect = chakram.expect

const namespace = config.username

describe('{namespace}/search/', () => {
  const search_uri = tools.get_request_uri(util.format('%s/search/', namespace))
  const schema = tools.get_schema('search', 'search/')

  it('GET search for admin should return admin', async () => {
    const query = '?q=admin'
    const response = await chakram.get(search_uri + query)
    expect(response).to.have.status(200)
    expect(response).to.have.schema(schema)
    expect(response.body.users.results[0].username).to.equal('admin')
  })
})
