import history from 'utils/history'
import { login as setToken } from 'utils/auth'
import LoginAPI from './api'
import { Dispatch } from 'redux'

export const LOGIN_REQUEST = 'LOGIN_REQUEST'
export type LOGIN_REQUEST = typeof LOGIN_REQUEST
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS'
export type LOGIN_SUCCESS = typeof LOGIN_SUCCESS
export const LOGIN_FAILURE = 'LOGIN_FAILURE'
export type LOGIN_FAILURE = typeof LOGIN_FAILURE

export const CLOSE_ERROR = 'CLOSE_ERROR'
export type CLOSE_ERROR = typeof CLOSE_ERROR

export const TOKEN_LOGIN_REQUEST = 'TOKEN_LOGIN_REQUEST'
export type TOKEN_LOGIN_REQUEST = typeof TOKEN_LOGIN_REQUEST
export const TOKEN_LOGIN_SUCCESS = 'TOKEN_LOGIN_SUCCESS'
export type TOKEN_LOGIN_SUCCESS = typeof TOKEN_LOGIN_SUCCESS
export const TOKEN_LOGIN_FAILURE = 'TOKEN_LOGIN_FAILURE'
export type TOKEN_LOGIN_FAILURE = typeof TOKEN_LOGIN_FAILURE

export interface LoginActions {
  type: LOGIN_REQUEST | LOGIN_SUCCESS | LOGIN_FAILURE
  data?: any
  error?: any
}
export interface CloseErrorAction {
  type: CLOSE_ERROR
}

export interface TokenLoginActions {
  type: TOKEN_LOGIN_REQUEST | TOKEN_LOGIN_SUCCESS | TOKEN_LOGIN_FAILURE
  data?: any
  error?: any
}

export const login = (values: any) => (dispatch: Dispatch<LoginActions>) => {
  function request(): LoginActions {
    return {
      type: LOGIN_REQUEST
    }
  }

  function success(data: any): LoginActions {
    return {
      type: LOGIN_SUCCESS,
      data
    }
  }

  function failure(error: any): LoginActions {
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
      dispatch(failure(error.response))
    }
  )
}

export const closeError = () => (dispatch: Dispatch) => {
  dispatch({
    type: CLOSE_ERROR
  })
}

export const tokenLogin = (tempToken: string) => (
  dispatch: Dispatch<TokenLoginActions>
) => {
  function request(): TokenLoginActions {
    return {
      type: TOKEN_LOGIN_REQUEST
    }
  }

  function success(data: any): TokenLoginActions {
    return {
      type: TOKEN_LOGIN_SUCCESS,
      data
    }
  }

  function failure(error: any): TokenLoginActions {
    return {
      type: TOKEN_LOGIN_FAILURE,
      error
    }
  }
  dispatch(request())
  return LoginAPI.tokenLogin(tempToken).then(
    response => {
      setToken(response.data.token, 'JWT')
      dispatch(success(response.data))
      history.push('/')
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}
