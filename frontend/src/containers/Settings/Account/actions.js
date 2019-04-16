import AccountSettingsAPI from './api'

export const CHANGE_PASSWORD_REQUEST = 'CHANGE_PASSWORD_REQUEST'
export const CHANGE_PASSWORD_SUCCESS = 'CHANGE_PASSWORD_SUCCESS'
export const CHANGE_PASSWORD_FAILURE = 'CHANGE_PASSWORD_FAILURE'
export const DELETE_ACCOUNT_REQUEST = 'DELETE_ACCOUNT_REQUEST'
export const DELETE_ACCOUNT_SUCCESS = 'DELETE_ACCOUNT_SUCCESS'
export const DELETE_ACCOUNT_FAILURE = 'DELETE_ACCOUNT_FAILURE'
export const UPDATE_PROFILE_REQUEST = 'UPDATE_PROFILE_REQUEST'
export const UPDATE_PROFILE_SUCCESS = 'UPDATE_PROFILE_SUCCESS'
export const UPDATE_PROFILE_FAILURE = 'UPDATE_PROFILEFAILURE'

export const updateProfile = (accountID, values) => dispatch => {
  function request() {
    return {
      type: UPDATE_PROFILE_REQUEST
    }
  }
  function success(data) {
    return {
      type: UPDATE_PROFILE_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: UPDATE_PROFILE_FAILURE
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

export const changePassword = (accountID, values) => dispatch => {
  function request() {
    return {
      type: CHANGE_PASSWORD_REQUEST
    }
  }
  function success(data) {
    return {
      type: CHANGE_PASSWORD_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: CHANGE_PASSWORD_FAILURE
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

export const deleteAccount = accountID => dispatch => {
  function request() {
    return {
      type: DELETE_ACCOUNT_REQUEST
    }
  }
  function success(data) {
    return {
      type: DELETE_ACCOUNT_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: DELETE_ACCOUNT_FAILURE
    }
  }
  dispatch(request())
  return AccountSettingsAPI.deleteAccount(accountID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
