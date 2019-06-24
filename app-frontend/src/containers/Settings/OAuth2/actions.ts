import OAuth2API from './api'
import { Dispatch } from 'redux'
import { reset } from 'redux-form'

export const GET_APPS_REQUEST = 'GET_APPS_REQUEST'
export type GET_APPS_REQUEST = typeof GET_APPS_REQUEST
export const GET_APPS_SUCCESS = 'GET_APPS_SUCCESS'
export type GET_APPS_SUCCESS = typeof GET_APPS_SUCCESS
export const GET_APPS_FAILURE = 'GET_APPS_FAILURE'
export type GET_APPS_FAILURE = typeof GET_APPS_FAILURE

export const NEW_APP_REQUEST = 'NEW_APP_REQUEST'
export type NEW_APP_REQUEST = typeof NEW_APP_REQUEST
export const NEW_APP_SUCCESS = 'NEW_APP_SUCCESS'
export type NEW_APP_SUCCESS = typeof NEW_APP_SUCCESS
export const NEW_APP_FAILURE = 'NEW_APP_FAILURE'
export type NEW_APP_FAILURE = typeof NEW_APP_FAILURE

export const DELETE_APP_REQUEST = 'DELETE_APP_REQUEST'
export type DELETE_APP_REQUEST = typeof DELETE_APP_REQUEST
export const DELETE_APP_SUCCESS = 'DELETE_APP_SUCCESS'
export type DELETE_APP_SUCCESS = typeof DELETE_APP_SUCCESS
export const DELETE_APP_FAILURE = 'DELETE_APP_FAILURE'
export type DELETE_APP_FAILURE = typeof DELETE_APP_FAILURE

export interface GetAppsActions {
  type: GET_APPS_REQUEST | GET_APPS_SUCCESS | GET_APPS_FAILURE
  data?: any
  error?: any
}

export interface NewAppActions {
  type: NEW_APP_REQUEST | NEW_APP_SUCCESS | NEW_APP_FAILURE
  data?: any
  error?: any
}

export interface DeleteAppActions {
  type: DELETE_APP_REQUEST | DELETE_APP_SUCCESS | DELETE_APP_FAILURE
  data?: any
  error?: any
}

export type OAuth2Actions = GetAppsActions & NewAppActions & DeleteAppActions

export const getApps = (username: string) => (
  dispatch: Dispatch<GetAppsActions>
) => {
  function request(): GetAppsActions {
    return {
      type: GET_APPS_REQUEST
    }
  }
  function success(data: any): GetAppsActions {
    return {
      type: GET_APPS_SUCCESS,
      data
    }
  }
  function failure(error: any): GetAppsActions {
    return {
      type: GET_APPS_FAILURE,
      error
    }
  }
  dispatch(request())
  return OAuth2API.getApps(username).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const createApp = (username: string, appName: string) => (
  dispatch: Dispatch<NewAppActions>
) => {
  function request(): NewAppActions {
    return {
      type: NEW_APP_REQUEST
    }
  }
  function success(data: any): NewAppActions {
    return {
      type: NEW_APP_SUCCESS,
      data
    }
  }
  function failure(error: any): NewAppActions {
    return {
      type: NEW_APP_FAILURE,
      error
    }
  }
  dispatch(request())
  return OAuth2API.createApp(username, appName).then(
    data => {
      dispatch(reset('newApp'))
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const deleteApp = (username: string, appID: string) => (
  dispatch: Dispatch<DeleteAppActions>
) => {
  function request(): DeleteAppActions {
    return {
      type: DELETE_APP_REQUEST
    }
  }
  function success(data: any): DeleteAppActions {
    return {
      type: DELETE_APP_SUCCESS,
      data
    }
  }
  function failure(error: any): DeleteAppActions {
    return {
      type: DELETE_APP_FAILURE,
      error
    }
  }
  dispatch(request())
  return OAuth2API.deleteApp(username, appID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}
