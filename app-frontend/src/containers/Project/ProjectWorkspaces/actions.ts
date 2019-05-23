import WorkspacesAPI from './api'
import { Dispatch } from 'redux'

export const GET_SIZES_REQUEST = 'GET_SIZES_REQUEST'
export type GET_SIZES_REQUEST = typeof GET_SIZES_REQUEST
export const GET_SIZES_SUCCESS = 'GET_SIZES_SUCCESS'
export type GET_SIZES_SUCCESS = typeof GET_SIZES_SUCCESS
export const GET_SIZES_FAILURE = 'GET_SIZES_FAILURE'
export type GET_SIZES_FAILURE = typeof GET_SIZES_FAILURE

export const GET_WORKSPACES_REQUEST = 'GET_WORKSPACES_REQUEST'
export type GET_WORKSPACES_REQUEST = typeof GET_WORKSPACES_REQUEST
export const GET_WORKSPACES_SUCCESS = 'GET_WORKSPACES_SUCCESS'
export type GET_WORKSPACES_SUCCESS = typeof GET_WORKSPACES_SUCCESS
export const GET_WORKSPACES_FAILURE = 'GET_WORKSPACES_FAILURE'
export type GET_WORKSPACES_FAILURE = typeof GET_WORKSPACES_FAILURE

export const START_SERVER_REQUEST = 'START_SERVER_REQUEST'
export type START_SERVER_REQUEST = typeof START_SERVER_REQUEST
export const START_SERVER_SUCCESS = 'START_SERVER_SUCCESS'
export type START_SERVER_SUCCESS = typeof START_SERVER_SUCCESS
export const START_SERVER_FAILURE = 'START_SERVER_FAILURE'
export type START_SERVER_FAILURE = typeof START_SERVER_FAILURE

export const STOP_SERVER_REQUEST = 'STOP_SERVER_REQUEST'
export type STOP_SERVER_REQUEST = typeof STOP_SERVER_REQUEST
export const STOP_SERVER_SUCCESS = 'STOP_SERVER_SUCCESS'
export type STOP_SERVER_SUCCESS = typeof STOP_SERVER_SUCCESS
export const STOP_SERVER_FAILURE = 'STOP_SERVER_FAILURE'
export type STOP_SERVER_FAILURE = typeof STOP_SERVER_FAILURE

export const DELETE_SERVER_REQUEST = 'DELETE_SERVER_REQUEST'
export type DELETE_SERVER_REQUEST = typeof DELETE_SERVER_REQUEST
export const DELETE_SERVER_SUCCESS = 'DELETE_SERVER_SUCCESS'
export type DELETE_SERVER_SUCCESS = typeof DELETE_SERVER_SUCCESS
export const DELETE_SERVER_FAILURE = 'DELETE_SERVER_FAILURE'
export type DELETE_SERVER_FAILURE = typeof DELETE_SERVER_FAILURE

export const UPDATE_STATUS = 'UPDATE_STATUS'
export type UPDATE_STATUS = typeof UPDATE_STATUS

export interface GetSizesActions {
  type: GET_SIZES_REQUEST | GET_SIZES_SUCCESS | GET_SIZES_FAILURE
  data?: any
  error?: any
}

export interface GetWorkspacesActions {
  type: GET_WORKSPACES_REQUEST | GET_WORKSPACES_SUCCESS | GET_WORKSPACES_FAILURE
  data?: any
  error?: any
}

export interface StartServerActions {
  type: START_SERVER_REQUEST | START_SERVER_SUCCESS | START_SERVER_FAILURE
  data?: any
  error?: any
}

export interface StopServerActions {
  type: STOP_SERVER_REQUEST | STOP_SERVER_SUCCESS | STOP_SERVER_FAILURE
  data?: any
  error?: any
}

export interface DeleteServerActions {
  type: DELETE_SERVER_REQUEST | DELETE_SERVER_SUCCESS | DELETE_SERVER_FAILURE
  data?: any
  error?: any
}

export interface UpdateStatusAction {
  type: UPDATE_STATUS
  data?: any
}

export const getServerSizes = () => (dispatch: Dispatch<GetSizesActions>) => {
  function request(): GetSizesActions {
    return {
      type: GET_SIZES_REQUEST
    }
  }
  function success(data: any): GetSizesActions {
    return {
      type: GET_SIZES_SUCCESS,
      data
    }
  }
  function failure(error: any): GetSizesActions {
    return {
      type: GET_SIZES_FAILURE,
      error
    }
  }
  dispatch(request())
  return WorkspacesAPI.getServerSizes().then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const getWorkspaces = (username: string, projectID: string) => (
  dispatch: Dispatch<GetWorkspacesActions>
) => {
  function request(): GetWorkspacesActions {
    return {
      type: GET_WORKSPACES_REQUEST
    }
  }
  function success(data: any): GetWorkspacesActions {
    return {
      type: GET_WORKSPACES_SUCCESS,
      data
    }
  }
  function failure(error: any): GetWorkspacesActions {
    return {
      type: GET_WORKSPACES_FAILURE,
      error
    }
  }
  dispatch(request())
  return WorkspacesAPI.getWorkspaces(username, projectID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const startServer = (
  username: string,
  projectID: string,
  workspaceID: string
) => (dispatch: Dispatch<StartServerActions>) => {
  function request(): StartServerActions {
    return {
      type: START_SERVER_REQUEST
    }
  }
  function success(data: any): StartServerActions {
    return {
      type: START_SERVER_SUCCESS,
      data
    }
  }
  function failure(error: any): StartServerActions {
    return {
      type: START_SERVER_FAILURE,
      error
    }
  }
  dispatch(request())
  return WorkspacesAPI.startServer(username, projectID, workspaceID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const stopServer = (
  username: string,
  projectID: string,
  workspaceID: string
) => (dispatch: Dispatch<StopServerActions>) => {
  function request(): StopServerActions {
    return {
      type: STOP_SERVER_REQUEST
    }
  }
  function success(data: any): StopServerActions {
    return {
      type: STOP_SERVER_SUCCESS,
      data
    }
  }
  function failure(error: any): StopServerActions {
    return {
      type: STOP_SERVER_FAILURE,
      error
    }
  }
  dispatch(request())
  return WorkspacesAPI.stopServer(username, projectID, workspaceID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const deleteServer = (
  username: string,
  projectID: string,
  workspaceID: string
) => (dispatch: Dispatch<DeleteServerActions>) => {
  function request(): DeleteServerActions {
    return {
      type: DELETE_SERVER_REQUEST
    }
  }
  function success(data: any): DeleteServerActions {
    return {
      type: DELETE_SERVER_SUCCESS,
      data
    }
  }
  function failure(error: any): DeleteServerActions {
    return {
      type: DELETE_SERVER_FAILURE,
      error
    }
  }
  dispatch(request())
  return WorkspacesAPI.deleteServer(username, projectID, workspaceID).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const updateStatus = (data: any) => (
  dispatch: Dispatch<UpdateStatusAction>
) => {
  dispatch({
    type: UPDATE_STATUS,
    data
  })
}
