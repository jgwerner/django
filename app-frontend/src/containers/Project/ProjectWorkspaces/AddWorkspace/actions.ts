import history from '../../../../utils/history'
import AddWorkspaceAPI from './api'
import { Dispatch } from 'redux'

export const ADD_WORKSPACE_REQUEST = 'ADD_WORKSPACE_REQUEST'
export type ADD_WORKSPACE_REQUEST = typeof ADD_WORKSPACE_REQUEST

export const ADD_WORKSPACE_SUCCESS = 'ADD_WORKSPACE_SUCCESS'
export type ADD_WORKSPACE_SUCCESS = typeof ADD_WORKSPACE_SUCCESS

export const ADD_WORKSPACE_FAILURE = 'ADD_WORKSPACE_FAILURE'
export type ADD_WORKSPACE_FAILURE = typeof ADD_WORKSPACE_FAILURE

export interface UpdateProjectActions {
  type: ADD_WORKSPACE_REQUEST | ADD_WORKSPACE_SUCCESS | ADD_WORKSPACE_FAILURE
  data?: any
  error?: any
}

export const addWorkspace = (
  username: string,
  server: any,
  projectID: string,
  values: any
) => (dispatch: Dispatch<UpdateProjectActions>) => {
  function request(): UpdateProjectActions {
    return {
      type: ADD_WORKSPACE_REQUEST
    }
  }
  function success(data: any): UpdateProjectActions {
    return {
      type: ADD_WORKSPACE_SUCCESS,
      data
    }
  }
  function failure(error: any): UpdateProjectActions {
    return {
      type: ADD_WORKSPACE_FAILURE,
      error
    }
  }
  dispatch(request())
  return AddWorkspaceAPI.addWorkspace(username, server, projectID, values).then(
    data => {
      dispatch(success(data))
      history.goBack()
    },
    error => {
      dispatch(failure(error.response))
    }
  )
}
