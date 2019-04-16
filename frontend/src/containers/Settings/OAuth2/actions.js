import OAuth2API from './api'

export const GET_APPS_REQUEST = 'GET_APPS_REQUEST'
export const GET_APPS_SUCCESS = 'GET_APPS_SUCCESS'
export const GET_APPS_FAILURE = 'GET_APPS_FAILURE'
export const NEW_APP_REQUEST = 'NEW_APP_REQUEST'
export const NEW_APP_SUCCESS = 'NEW_APP_SUCCESS'
export const NEW_APP_FAILURE = 'NEW_APP_FAILURE'
export const DELETE_APP_REQUEST = 'DELETE_APP_REQUEST'
export const DELETE_APP_SUCCESS = 'DELETE_APP_SUCCESS'
export const DELETE_APP_FAILURE = 'DELETE_APP_FAILURE'

export const getApps = username => dispatch => {
  function request() {
    return {
      type: GET_APPS_REQUEST
    }
  }
  function success(data) {
    return {
      type: GET_APPS_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: GET_APPS_FAILURE
    }
  }
  dispatch(request())
  return OAuth2API.getApps(username).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const createApp = (username, appName) => dispatch => {
  function request() {
    return {
      type: NEW_APP_REQUEST
    }
  }
  function success(data) {
    return {
      type: NEW_APP_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: NEW_APP_FAILURE
    }
  }
  dispatch(request())
  return OAuth2API.createApp(username, appName).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const deleteApp = (username, appID) => dispatch => {
  function request() {
    return {
      type: DELETE_APP_REQUEST
    }
  }
  function success(data) {
    return {
      type: DELETE_APP_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: DELETE_APP_FAILURE
    }
  }
  dispatch(request())
  return OAuth2API.deleteApp(username, appID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
