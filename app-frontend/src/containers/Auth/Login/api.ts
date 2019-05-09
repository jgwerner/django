import axios from 'axios'

class LoginAPI {
  login = (values: { username: string; password: string }) => {
    const URL = `${process.env.REACT_APP_API_URL}auth/jwt-token-auth/`
    const body = {
      username: values.username,
      password: values.password
    }
    const headers = { 'Content-Type': 'application/json' }
    return axios
      .post(URL, body, {
        headers
      })
      .then(response => {
        return response
      })
      .catch(error => {
        throw error
      })
  }
}

export default new LoginAPI()
