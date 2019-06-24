import axios from 'axios'
import { getToken } from 'utils/auth'

class AccountSettingsAPI {
  changePassword = (accountID: string, values: { password: string }) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/users/profiles/${accountID}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      password: values.password
    }
    return axios
      .patch(URL, body, { headers })
      .then(response => response.data)
      .catch(error => {
        throw error
      })
  }

  deleteAccount = (accountID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/users/profiles/${accountID}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .delete(URL, { headers })
      .then(response => response.data)
      .catch(error => {
        throw error
      })
  }
}

export default new AccountSettingsAPI()
