import history from '../../../utils/history'
import AddProjectAPI from './api'
import { Dispatch } from 'redux';

export const ADD_PROJECT_REQUEST = 'ADD_PROJECT_REQUEST'
export type ADD_PROJECT_REQUEST = typeof ADD_PROJECT_REQUEST

export const ADD_PROJECT_SUCCESS = 'ADD_PROJECT_SUCCESS'
export type ADD_PROJECT_SUCCESS = typeof ADD_PROJECT_SUCCESS

export const ADD_PROJECT_FAILURE = 'ADD_PROJECT_FAILURE'
export type ADD_PROJECT_FAILURE = typeof ADD_PROJECT_FAILURE

export interface AddProjectActions {
  type: ADD_PROJECT_REQUEST | ADD_PROJECT_SUCCESS | ADD_PROJECT_FAILURE,
  data?: any,
  error?: any
}


export const addProject = (username: string, values: any) => (dispatch: Dispatch<AddProjectActions>) => {
  function request(): AddProjectActions {
    return {
      type: ADD_PROJECT_REQUEST
    }
  }
  function success(data: any): AddProjectActions {
    return {
      type: ADD_PROJECT_SUCCESS,
      data
    }
  }
  function failure(error: any): AddProjectActions {
    return {
      type: ADD_PROJECT_FAILURE,
      error
    }
  }
  dispatch(request())
  return AddProjectAPI.addProject(username, values).then(
    data => {
      dispatch(success(data))
      history.push('/')
    },
    error => {
      dispatch(failure(error))
    }
  )
}