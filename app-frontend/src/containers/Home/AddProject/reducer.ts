import {
  ADD_PROJECT_REQUEST,
  ADD_PROJECT_SUCCESS,
  ADD_PROJECT_FAILURE,
  CLOSE_ERROR
} from './actions'
import { AnyAction } from 'redux'

export interface AddProjectProps {
  newProjectSuccess: boolean
  newProjectError: boolean
}

const initialState = {
  newProjectSuccess: false,
  newProjectError: false
}

const addProject = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case ADD_PROJECT_REQUEST:
      return {
        ...state,
        projects: []
      }
    case ADD_PROJECT_SUCCESS:
      return {
        ...state,
        newProjectSuccess: true
      }
    case ADD_PROJECT_FAILURE:
      return {
        ...state,
        newProjectError: true
      }
    case CLOSE_ERROR:
      return {
        ...state,
        newProjectError: false
      }
    default:
      return state
  }
}

export default addProject
