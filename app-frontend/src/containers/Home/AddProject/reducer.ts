import {
  ADD_PROJECT_REQUEST,
  ADD_PROJECT_SUCCESS,
  ADD_PROJECT_FAILURE,
  CLOSE_ERROR,
  CLOSE_SUCCESS
} from './actions'
import { AnyAction } from 'redux'

export interface AddProjectProps {
  createProjectSuccess: boolean
  createProjectError: boolean
  createProjectErrorMessage: string
}

export const initialState = {
  createProjectSuccess: false,
  createProjectError: false,
  createProjectErrorMessage: ''
}

const addProject = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case ADD_PROJECT_REQUEST:
      return {
        ...state
      }
    case ADD_PROJECT_SUCCESS:
      return {
        ...state,
        createProjectSuccess: true
      }
    case ADD_PROJECT_FAILURE:
      return {
        ...state,
        createProjectError: true,
        createProjectErrorMessage: action.error.data.name
          ? action.error.data.name[0]
          : 'Error creating project'
      }
    case CLOSE_ERROR:
      return {
        ...state,
        createProjectError: false
      }
    case CLOSE_SUCCESS:
      return {
        ...state,
        createProjectSuccess: false
      }
    default:
      return state
  }
}

export default addProject
