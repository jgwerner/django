import history from 'utils/history'
import UpdateProjectAPI from './api'
import { Dispatch } from 'redux'

export const UPDATE_PROJECT_REQUEST = 'UPDATE_PROJECT_REQUEST'
export type UPDATE_PROJECT_REQUEST = typeof UPDATE_PROJECT_REQUEST
export const UPDATE_PROJECT_SUCCESS = 'UPDATE_PROJECT_SUCCESS'
export type UPDATE_PROJECT_SUCCESS = typeof UPDATE_PROJECT_SUCCESS
export const UPDATE_PROJECT_FAILURE = 'UPDATE_PROJECT_FAILURE'
export type UPDATE_PROJECT_FAILURE = typeof UPDATE_PROJECT_FAILURE

export const CHANGE_VISIBILITY_REQUEST = 'CHANGE_VISIBILITY_REQUEST'
export type CHANGE_VISIBILITY_REQUEST = typeof CHANGE_VISIBILITY_REQUEST
export const CHANGE_VISIBILITY_SUCCESS = 'CHANGE_VISIBILITY_SUCCESS'
export type CHANGE_VISIBILITY_SUCCESS = typeof CHANGE_VISIBILITY_SUCCESS
export const CHANGE_VISIBILITY_FAILURE = 'CHANGE_VISIBILITY_FAILURE'
export type CHANGE_VISIBILITY_FAILURE = typeof CHANGE_VISIBILITY_FAILURE

export const DELETE_PROJECT_REQUEST = 'DELETE_PROJECT_REQUEST'
export type DELETE_PROJECT_REQUEST = typeof DELETE_PROJECT_REQUEST
export const DELETE_PROJECT_SUCCESS = 'DELETE_PROJECT_SUCCESS'
export type DELETE_PROJECT_SUCCESS = typeof DELETE_PROJECT_SUCCESS
export const DELETE_PROJECT_FAILURE = 'DELETE_PROJECT_FAILURE'
export type DELETE_PROJECT_FAILURE = typeof DELETE_PROJECT_FAILURE

export const CLOSE_ERROR = 'CLOSE_ERROR'
export type CLOSE_ERROR = typeof CLOSE_ERROR

export const CLOSE_SUCCESS = 'CLOSE_SUCCESS'
export type CLOSE_SUCCESS = typeof CLOSE_SUCCESS

export interface UpdateProjectActions {
  type: UPDATE_PROJECT_REQUEST | UPDATE_PROJECT_SUCCESS | UPDATE_PROJECT_FAILURE
  data?: any
  error?: any
}

export interface ChangeVisibilityActions {
  type:
    | CHANGE_VISIBILITY_REQUEST
    | CHANGE_VISIBILITY_SUCCESS
    | CHANGE_VISIBILITY_FAILURE
  data?: any
  error?: any
}

export interface DeleteProjectActions {
  type: DELETE_PROJECT_REQUEST | DELETE_PROJECT_SUCCESS | DELETE_PROJECT_FAILURE
  data?: any
  error?: any
}

export interface CloseErrorAction {
  type: CLOSE_ERROR
}

export interface CloseSuccessAction {
  type: CLOSE_SUCCESS
}

export const updateProject = (
  username: string,
  projectID: string,
  values: any
) => (dispatch: Dispatch<UpdateProjectActions>) => {
  function request(): UpdateProjectActions {
    return {
      type: UPDATE_PROJECT_REQUEST
    }
  }
  function success(data: any): UpdateProjectActions {
    return {
      type: UPDATE_PROJECT_SUCCESS,
      data
    }
  }
  function failure(error: any): UpdateProjectActions {
    return {
      type: UPDATE_PROJECT_FAILURE,
      error
    }
  }
  dispatch(request())
  return UpdateProjectAPI.updateDetails(username, projectID, values).then(
    data => {
      dispatch(success(data))
      history.push(`/${username}/${values.name}/settings`)
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const changeVisibility = (
  username: string,
  projectName: string,
  visibility: any
) => (dispatch: Dispatch<ChangeVisibilityActions>) => {
  function request(): ChangeVisibilityActions {
    return {
      type: CHANGE_VISIBILITY_REQUEST
    }
  }
  function success(data: any): ChangeVisibilityActions {
    return {
      type: CHANGE_VISIBILITY_SUCCESS,
      data
    }
  }
  function failure(error: any): ChangeVisibilityActions {
    return {
      type: CHANGE_VISIBILITY_FAILURE,
      error
    }
  }
  dispatch(request())
  return UpdateProjectAPI.changeVisibility(
    username,
    projectName,
    visibility
  ).then(
    data => {
      dispatch(success(data))
      history.goBack()
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}

export const deleteProject = (username: string, projectName: string) => (
  dispatch: Dispatch<DeleteProjectActions>
) => {
  function request(): DeleteProjectActions {
    return {
      type: DELETE_PROJECT_REQUEST
    }
  }
  function success(data: any): DeleteProjectActions {
    return {
      type: DELETE_PROJECT_SUCCESS,
      data
    }
  }
  function failure(error: any): DeleteProjectActions {
    return {
      type: DELETE_PROJECT_FAILURE,
      error
    }
  }
  dispatch(request())
  return UpdateProjectAPI.deleteProject(username, projectName).then(
    data => {
      dispatch(success(data))
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

export const closeSuccess = () => (dispatch: Dispatch) => {
  dispatch({
    type: CLOSE_SUCCESS
  })
}
