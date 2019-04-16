import history from 'utils/history'
import { login as setToken } from 'utils/auth'
import LoginAPI from './api'

export const LOGIN_REQUEST = 'LOGIN_REQUEST'
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS'
export const LOGIN_FAILURE = 'LOGIN_FAILURE'

export const login = values => dispatch => {
  function request() {
    return {
      type: LOGIN_REQUEST
    }
  }

  function success(data) {
    return {
      type: LOGIN_SUCCESS,
      data
    }
  }

  function failure(error) {
    return {
      type: LOGIN_FAILURE,
      error
    }
  }
  dispatch(request())
  return LoginAPI.login(values).then(
    response => {
      setToken(response.data.token, 'JWT')
      dispatch(success(response.data))
      history.push('/')
    },
    error => {
      dispatch(failure(error))
    }
  )
}
