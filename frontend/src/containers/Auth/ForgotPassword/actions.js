import history from 'utils/history'
import ForgotPasswordAPI from './api'

export const RESET_PASSWORD_REQUEST = 'RESET_PASSWORD_REQUEST'
export const RESET_PASSWORD_SUCCESS = 'RESET_PASSWORD_SUCCESS'
export const RESET_PASSWORD_FAILURE = 'RESET_PASSWORD_FAILURE'
export const CONFIRM_PASSWORD_REQUEST = 'CONFIRM_PASSWORD_REQUEST'
export const CONFIRM_PASSWORD_SUCCESS = 'CONFIRM_PASSWORD_SUCCESS'
export const CONFIRM_PASSWORD_FAILURE = 'CONFIRM_PASSWORD_FAILURE'

export const resetPassword = values => dispatch => {
  function request() {
    return {
      type: RESET_PASSWORD_REQUEST
    }
  }

  function success() {
    return {
      type: RESET_PASSWORD_SUCCESS
    }
  }

  function failure(error) {
    return {
      type: RESET_PASSWORD_FAILURE,
      error
    }
  }
  dispatch(request())
  ForgotPasswordAPI.resetPassword(values).then(
    response => {
      dispatch(success(response))
      history.push('/password/next')
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const resetPasswordConfirm = (params, values) => dispatch => {
  function request() {
    return {
      type: CONFIRM_PASSWORD_REQUEST
    }
  }

  function success() {
    return {
      type: CONFIRM_PASSWORD_SUCCESS
    }
  }

  function failure(error) {
    return {
      type: CONFIRM_PASSWORD_FAILURE,
      error
    }
  }
  dispatch(request())
  ForgotPasswordAPI.resetPasswordConfirm(params, values).then(
    response => {
      dispatch(success(response))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}
