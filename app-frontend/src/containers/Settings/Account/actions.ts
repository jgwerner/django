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

export const UPDATE_PROFILE_REQUEST = 'UPDATE_PROFILE_REQUEST'
export type UPDATE_PROFILE_REQUEST = typeof UPDATE_PROFILE_REQUEST
export const UPDATE_PROFILE_SUCCESS = 'UPDATE_PROFILE_SUCCESS'
export type UPDATE_PROFILE_SUCCESS = typeof UPDATE_PROFILE_SUCCESS
export const UPDATE_PROFILE_FAILURE = 'UPDATE_PROFILEFAILURE'
export type UPDATE_PROFILE_FAILURE = typeof UPDATE_PROFILE_FAILURE

export const CLOSE_PROFILE_SUCCESS = 'CLOSE_PROFILE_SUCCESS'
export type CLOSE_PROFILE_SUCCESS = typeof CLOSE_PROFILE_SUCCESS
export const CLOSE_PROFILE_ERROR = 'CLOSE_PROFILE_ERROR'
export type CLOSE_PROFILE_ERROR = typeof CLOSE_PROFILE_ERROR

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

export interface UpdateProfileActions {
  type: UPDATE_PROFILE_REQUEST | UPDATE_PROFILE_SUCCESS | UPDATE_PROFILE_FAILURE
  data?: any
  error?: any
}

export interface CloseBannerActions {
  type:
    | CLOSE_PROFILE_SUCCESS
    | CLOSE_PROFILE_ERROR
    | CLOSE_PASSWORD_SUCCESS
    | CLOSE_PASSWORD_ERROR
}

export type AccountSettingsActions = ChangePasswordActions &
  DeleteAccountActions &
  UpdateProfileActions &
  CloseBannerActions

export const updateProfile = (
  accountID: string,
  values: { firstName: string; lastName: string; email: string }
) => (dispatch: Dispatch<UpdateProfileActions>) => {
  function request(): UpdateProfileActions {
    return {
      type: UPDATE_PROFILE_REQUEST
    }
  }
  function success(data: any): UpdateProfileActions {
    return {
      type: UPDATE_PROFILE_SUCCESS,
      data
    }
  }
  function failure(error: any): UpdateProfileActions {
    return {
      type: UPDATE_PROFILE_FAILURE,
      error
    }
  }
  dispatch(request())
  return AccountSettingsAPI.updateProfile(accountID, values).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

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
      dispatch(failure(error))
    }
  )
}

export const closeProfileSuccess = () => (
  dispatch: Dispatch<CloseBannerActions>
) => {
  dispatch({
    type: CLOSE_PROFILE_SUCCESS
  })
}

export const closeProfileError = () => (
  dispatch: Dispatch<CloseBannerActions>
) => {
  dispatch({
    type: CLOSE_PROFILE_ERROR
  })
}

export const closePasswordSuccess = () => (
  dispatch: Dispatch<CloseBannerActions>
) => {
  dispatch({
    type: CLOSE_PASSWORD_SUCCESS
  })
}

export const closePasswordError = () => (
  dispatch: Dispatch<CloseBannerActions>
) => {
  dispatch({
    type: CLOSE_PASSWORD_ERROR
  })
}

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
      dispatch(failure(error))
    }
  )
}
