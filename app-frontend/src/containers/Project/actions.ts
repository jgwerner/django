import ProjectAPI from './api'
import { Dispatch } from 'redux'

export const PROJECT_DETAILS_REQUEST = 'PROJECT_DETAILS_REQUEST'
export type PROJECT_DETAILS_REQUEST = typeof PROJECT_DETAILS_REQUEST
export const PROJECT_DETAILS_SUCCESS = 'PROJECT_DETAILS_SUCCESS'
export type PROJECT_DETAILS_SUCCESS = typeof PROJECT_DETAILS_SUCCESS
export const PROJECT_DETAILS_FAILURE = 'PROJECT_DETAILS_FAILURE'
export type PROJECT_DETAILS_FAILURE = typeof PROJECT_DETAILS_FAILURE

export interface ProjectDetailsActions {
  type:
    | PROJECT_DETAILS_REQUEST
    | PROJECT_DETAILS_SUCCESS
    | PROJECT_DETAILS_FAILURE
  data?: any
  error?: any
}

export const getProject = (username: string, projectName: string) => (
  dispatch: Dispatch<ProjectDetailsActions>
) => {
  function request(): ProjectDetailsActions {
    return {
      type: PROJECT_DETAILS_REQUEST
    }
  }
  function success(data: any): ProjectDetailsActions {
    return {
      type: PROJECT_DETAILS_SUCCESS,
      data
    }
  }
  function failure(error: any): ProjectDetailsActions {
    return {
      type: PROJECT_DETAILS_FAILURE,
      error
    }
  }
  dispatch(request())
  return ProjectAPI.getProject(username, projectName).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
