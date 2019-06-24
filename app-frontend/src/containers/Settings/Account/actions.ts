import AccountSettingsAPI from './api'
import { Dispatch } from 'redux'
import history from 'utils/history'

export const CHANGE_PASSWORD_REQUEST = 'CHANGE_PASSWORD_REQUEST'
export type CHANGE_PASSWORD_REQUEST = typeof CHANGE_PASSWORD_REQUEST
export const CHANGE_PASSWORD_SUCCESS = 'CHANGE_PASSWORD_SUCCESS'
export type CHANGE_PASSWORD_SUCCESS = typeof CHANGE_PASSWORD_SUCCESS
export const CHANGE_PASSWORD_FAILURE = 'CHANGE_PASSWORD_FAILURE'
export type CHANGE_PASSWORD_FAILURE = typeof CHANGE_PASSWORD_FAILURE

export const DELETE_ACCOUNT_REQUEST = 'DELETE_ACCOUNT_REQUEST'
export type DELETE_ACCOUNT_REQUEST = typeof DELETE_ACCOUNT_REQUEST
export const DELETE_ACCOUNT_SUCCESS = 'DELETE_ACCOUNT_SUCCESS'
export type DELETE_ACCOUNT_SUCCESS = typeof DELETE_ACCOUNT_SUCCESS
export const DELETE_ACCOUNT_FAILURE = 'DELETE_ACCOUNT_FAILURE'
export type DELETE_ACCOUNT_FAILURE = typeof DELETE_ACCOUNT_FAILURE

export const CLOSE_PASSWORD_SUCCESS = 'CLOSE_PASSWORD_SUCCESS'
export type CLOSE_PASSWORD_SUCCESS = typeof CLOSE_PASSWORD_SUCCESS
export const CLOSE_PASSWORD_ERROR = 'CLOSE_PASSWORD_ERROR'
export type CLOSE_PASSWORD_ERROR = typeof CLOSE_PASSWORD_ERROR

export interface ChangePasswordActions {
  type:
    | CHANGE_PASSWORD_REQUEST
    | CHANGE_PASSWORD_SUCCESS
    | CHANGE_PASSWORD_FAILURE
  data?: any
  error?: any
}

export interface DeleteAccountActions {
  type: DELETE_ACCOUNT_REQUEST | DELETE_ACCOUNT_SUCCESS | DELETE_ACCOUNT_FAILURE
  data?: any
  error?: any
}

export interface CloseBannerActions {
  type: CLOSE_PASSWORD_SUCCESS | CLOSE_PASSWORD_ERROR
}

export type AccountSettingsActions = ChangePasswordActions &
  DeleteAccountActions &
  CloseBannerActions

export const changePassword = (
  accountID: string,
  values: { password: string }
) => (dispatch: Dispatch<ChangePasswordActions>) => {
  function request(): ChangePasswordActions {
    return {
      type: CHANGE_PASSWORD_REQUEST
    }
  }
  function success(data: any): ChangePasswordActions {
    return {
      type: CHANGE_PASSWORD_SUCCESS,
      data
    }
  }
  function failure(error: any): ChangePasswordActions {
    return {
      type: CHANGE_PASSWORD_FAILURE,
      error
    }
  }
  dispatch(request())
  return AccountSettingsAPI.changePassword(accountID, values).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const closePasswordSuccess = () => ({
  type: CLOSE_PASSWORD_SUCCESS
})

export const closePasswordError = () => ({
  type: CLOSE_PASSWORD_ERROR
})

export const deleteAccount = (accountID: string) => (
  dispatch: Dispatch<DeleteAccountActions>
) => {
  function request(): DeleteAccountActions {
    return {
      type: DELETE_ACCOUNT_REQUEST
    }
  }
  function success(data: any): DeleteAccountActions {
    return {
      type: DELETE_ACCOUNT_SUCCESS,
      data
    }
  }
  function failure(error: any): DeleteAccountActions {
    return {
      type: DELETE_ACCOUNT_FAILURE,
      error
    }
  }
  dispatch(request())
  return AccountSettingsAPI.deleteAccount(accountID).then(
    data => {
      dispatch(success(data))
      history.push('/auth')
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}
