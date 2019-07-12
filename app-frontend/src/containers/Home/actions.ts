import history from 'utils/history'
import HomeAPI from './api'
import { Dispatch } from 'redux'

export const USER_INFO_REQUEST = 'USER_INFO_REQUEST'
export type USER_INFO_REQUEST = typeof USER_INFO_REQUEST

export const USER_INFO_SUCCESS = 'USER_INFO_SUCCESS'
export type USER_INFO_SUCCESS = typeof USER_INFO_SUCCESS

export const USER_INFO_FAILURE = 'USER_INFO_FAILURE'
export type USER_INFO_FAILURE = typeof USER_INFO_FAILURE

export const LOGOUT = 'LOGOUT'
export type LOGOUT = typeof LOGOUT

export interface HomeActions {
  type: USER_INFO_REQUEST | USER_INFO_SUCCESS | USER_INFO_FAILURE
  data?: any
  error?: any
}

export interface LogoutAction {
  type: LOGOUT
}

export const getUserInfo = () => (dispatch: Dispatch<HomeActions>) => {
  function request(): HomeActions {
    return {
      type: USER_INFO_REQUEST
    }
  }
  function success(data: any): HomeActions {
    return {
      type: USER_INFO_SUCCESS,
      data
    }
  }
  function failure(error: any): HomeActions {
    return {
      type: USER_INFO_FAILURE,
      error
    }
  }
  dispatch(request())
  return HomeAPI.getUserInfo().then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const logout = () => (dispatch: Dispatch<LogoutAction>) => {
  dispatch({
    type: LOGOUT
  })
  localStorage.clear()
  history.push('/auth')
}
