import axios from 'axios'
import { getToken } from 'utils/auth'

class AccountSettingsAPI {
  changePassword = (accountID, values) => {
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
      .then(response => response)
      .catch(error => error)
  }

  updateProfile = (accountID, values) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/users/profiles/${accountID}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      firstName: values.firstName,
      lastName: values.lastName,
      email: values.email
    }
    return axios
      .patch(URL, body, { headers })
      .then(response => response)
      .catch(error => error)
  }

  deleteAccount = () => {}
}

export default new AccountSettingsAPI()
