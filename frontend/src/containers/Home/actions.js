import history from 'utils/history'
import HomeAPI from './api'

export const USER_INFO_REQUEST = 'USER_INFO_REQUEST'
export const USER_INFO_SUCCESS = 'USER_INFO_SUCCESS'
export const USER_INFO_FAILURE = 'USER_INFO_FAILURE'
export const LOGOUT = 'LOGOUT'

export const getUserInfo = () => dispatch => {
  function request() {
    return {
      type: USER_INFO_REQUEST
    }
  }
  function success(data) {
    return {
      type: USER_INFO_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: USER_INFO_FAILURE
    }
  }
  dispatch(request())
  return HomeAPI.getUserInfo().then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const logout = () => dispatch => {
  dispatch({
    type: LOGOUT
  })
  localStorage.clear()
  history.push('/auth')
}
