const chakram = require('chakram')
const util = require('util')
const config = require('../config')
const tools = require('../test_utils')
const expect = chakram.expect

const namespace = config.username

describe('{namespace}/notifications/', () => {
  const notifications_uri = tools.get_request_uri(util.format('%s/notifications/', namespace))
})

// todo