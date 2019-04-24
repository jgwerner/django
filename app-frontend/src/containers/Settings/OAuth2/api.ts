import axios from 'axios'
import { getToken } from '../../../utils/auth'

class OAuth2API {
  getApps = (username: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/oauth/applications/
    `
    const headers = {
      Authorization: getToken()
    }
    return axios
      .get(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  createApp = (username: string, name: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/oauth/applications/
    `
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      name,
      client_type: 'public',
      authorization_grant_type: 'password'
    }
    return axios
      .post(URL, body, { headers })
      .then(response => response)
      .catch(error => error)
  }

  deleteApp = (username: string, appID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/oauth/applications/${appID}
    `
    const headers = {
      Authorization: getToken()
    }
    return axios
      .delete(URL, { headers })
      .then(response => response)
      .catch(error => error)
  }
}

export default new OAuth2API()
