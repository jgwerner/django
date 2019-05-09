import ProjectListAPI from './api'
import { Dispatch } from 'redux'

export const PROJECT_LIST_REQUEST = 'PROJECT_LIST_REQUEST'
export type PROJECT_LIST_REQUEST = typeof PROJECT_LIST_REQUEST
export const PROJECT_LIST_SUCCESS = 'PROJECT_LIST_SUCCESS'
export type PROJECT_LIST_SUCCESS = typeof PROJECT_LIST_SUCCESS
export const PROJECT_LIST_FAILURE = 'PROJECT_LIST_FAILURE'
export type PROJECT_LIST_FAILURE = typeof PROJECT_LIST_FAILURE

export interface ProjectListRequest {
  type: PROJECT_LIST_REQUEST
}

export interface ProjectListSuccess {
  type: PROJECT_LIST_SUCCESS
  data: any
}

export interface ProjectListFailure {
  type: PROJECT_LIST_FAILURE
  error: any
}

export type ProjectListAction =
  | ProjectListRequest
  | ProjectListSuccess
  | ProjectListFailure

export const getProjectList = (username: string) => (
  dispatch: Dispatch<ProjectListAction>
) => {
  function request(): ProjectListRequest {
    return {
      type: PROJECT_LIST_REQUEST
    }
  }
  function success(data: any): ProjectListSuccess {
    return {
      type: PROJECT_LIST_SUCCESS,
      data
    }
  }
  function failure(error: any): ProjectListFailure {
    return {
      type: PROJECT_LIST_FAILURE,
      error
    }
  }
  dispatch(request())
  return ProjectListAPI.getProjectList(username).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
