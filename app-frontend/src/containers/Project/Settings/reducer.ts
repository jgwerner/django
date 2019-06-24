import {
  UPDATE_PROJECT_REQUEST,
  UPDATE_PROJECT_SUCCESS,
  UPDATE_PROJECT_FAILURE,
  DELETE_PROJECT_REQUEST,
  DELETE_PROJECT_SUCCESS,
  DELETE_PROJECT_FAILURE,
  CHANGE_VISIBILITY_REQUEST,
  CHANGE_VISIBILITY_SUCCESS,
  CHANGE_VISIBILITY_FAILURE
} from './actions'
import { AnyAction } from 'redux'

export interface SettingsStoreState {
  projectDetails: any
  results: any
}

export const initialState = {
  projectDetails: {}
}

const settings = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case UPDATE_PROJECT_REQUEST:
      return {
        ...state
      }
    case UPDATE_PROJECT_SUCCESS:
      return {
        ...state,
        projectDetails: action.data[0]
      }
    case UPDATE_PROJECT_FAILURE:
      return {
        ...state
      }
    case CHANGE_VISIBILITY_REQUEST:
      return {
        ...state
      }
    case CHANGE_VISIBILITY_SUCCESS:
      return {
        ...state,
        projectDetails: action.data[0]
      }
    case CHANGE_VISIBILITY_FAILURE:
      return {
        ...state
      }
    case DELETE_PROJECT_REQUEST:
      return {
        ...state
      }
    case DELETE_PROJECT_SUCCESS:
      return {
        ...state
      }
    case DELETE_PROJECT_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default settings
