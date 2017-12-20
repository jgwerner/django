const request = require('request-promise')
const util = require('util')
const config = require('./config')

let login = async (username, password) => {
  let uri = get_request_uri('auth/jwt-token-auth/', true)
  let options = {
    uri: uri,
    json: {
      username: username,
      password: password,
    },
  }
  const response = await request.post(uri, options)
  if (!response || !response.token) {
    throw new Error('Something went wrong when logging in. No token found.')
  }
  return response.token
}

let getToken = async (username, password, refresh = false) => {
  if (refresh) {
    global.token = undefined
  }
  if (!global.token) {
    console.log('Attempting to login...')
    try {
      global.token = await login(username, password)
    } catch (ex) {
      console.log('Login failed...')
      console.log(ex)
    }
  }
  return global.token
}

let get_request_uri = (api_path, exclude_version = false) => {
  let uri = util.format('%s:%s/%s/%s', config.host, config.port, config.version, api_path)
  if (exclude_version) {
    uri = uri.replace('/' + config.version, '')
  }
  return uri
}

module.exports = {
  login: getToken,
  get_request_uri: get_request_uri,
}
