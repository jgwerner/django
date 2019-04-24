import axios from 'axios'

class ForgotPasswordAPI {
  resetPassword = (values: {username: string, password: string} ) => {
    const URL = `${process.env.REACT_APP_API_URL}auth/password/reset/`
    const body = {
      username: values.username,
      password: values.password
    }
    const headers = { 'Content-Type': 'application/json' }
    return axios
      .post(URL, body, { headers })
      .then(response => response)
      .catch(error => {
        throw error
      })
  }

  resetPasswordConfirm = (params: {uid: string, token: string}, values: {password: string}) => {
    const URL = `${process.env.REACT_APP_API_URL}auth/password/reset/confirm/`
    const body = {
      uid: params.uid,
      token: params.token,
      new_password: values.password
    }
    const headers = { 'Content-Type': 'application/json' }
    return axios
      .post(URL, body, { headers })
      .then(response => response)
      .catch(error => {
        throw error
      })
  }
}

export default new ForgotPasswordAPI()
