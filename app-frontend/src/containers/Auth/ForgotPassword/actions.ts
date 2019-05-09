import history from '../../../utils/history'
import ForgotPasswordAPI from './api'
import { Dispatch } from 'redux'

export const RESET_PASSWORD_REQUEST = 'RESET_PASSWORD_REQUEST'
export type RESET_PASSWORD_REQUEST = typeof RESET_PASSWORD_REQUEST
export const RESET_PASSWORD_SUCCESS = 'RESET_PASSWORD_SUCCESS'
export type RESET_PASSWORD_SUCCESS = typeof RESET_PASSWORD_SUCCESS

export const RESET_PASSWORD_FAILURE = 'RESET_PASSWORD_FAILURE'
export type RESET_PASSWORD_FAILURE = typeof RESET_PASSWORD_FAILURE

export const CONFIRM_PASSWORD_REQUEST = 'CONFIRM_PASSWORD_REQUEST'
export type CONFIRM_PASSWORD_REQUEST = typeof CONFIRM_PASSWORD_REQUEST

export const CONFIRM_PASSWORD_SUCCESS = 'CONFIRM_PASSWORD_SUCCESS'
export type CONFIRM_PASSWORD_SUCCESS = typeof CONFIRM_PASSWORD_SUCCESS

export const CONFIRM_PASSWORD_FAILURE = 'CONFIRM_PASSWORD_FAILURE'
export type CONFIRM_PASSWORD_FAILURE = typeof CONFIRM_PASSWORD_FAILURE

export interface ResetPasswordActions {
  type: RESET_PASSWORD_REQUEST | RESET_PASSWORD_SUCCESS | RESET_PASSWORD_FAILURE
  response?: any
  error?: any
}

export interface ResetPasswordConfirmActions {
  type:
    | CONFIRM_PASSWORD_REQUEST
    | CONFIRM_PASSWORD_SUCCESS
    | CONFIRM_PASSWORD_FAILURE
  response?: any
  error?: any
}

export const resetPassword = (values: any) => (
  dispatch: Dispatch<ResetPasswordActions>
) => {
  function request(): ResetPasswordActions {
    return {
      type: RESET_PASSWORD_REQUEST
    }
  }

  function success(response: any): ResetPasswordActions {
    return {
      type: RESET_PASSWORD_SUCCESS,
      response
    }
  }

  function failure(error: any): ResetPasswordActions {
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

export const resetPasswordConfirm = (params: any, values: any) => (
  dispatch: Dispatch<ResetPasswordConfirmActions>
) => {
  function request(): ResetPasswordConfirmActions {
    return {
      type: CONFIRM_PASSWORD_REQUEST
    }
  }

  function success(response: any): ResetPasswordConfirmActions {
    return {
      type: CONFIRM_PASSWORD_SUCCESS,
      response
    }
  }

  function failure(error: any): ResetPasswordConfirmActions {
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
