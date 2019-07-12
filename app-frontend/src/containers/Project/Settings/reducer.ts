import {
  UPDATE_PROJECT_REQUEST,
  UPDATE_PROJECT_SUCCESS,
  UPDATE_PROJECT_FAILURE,
  DELETE_PROJECT_REQUEST,
  DELETE_PROJECT_SUCCESS,
  DELETE_PROJECT_FAILURE,
  CHANGE_VISIBILITY_REQUEST,
  CHANGE_VISIBILITY_SUCCESS,
  CHANGE_VISIBILITY_FAILURE,
  CLOSE_ERROR,
  CLOSE_SUCCESS
} from './actions'
import { AnyAction } from 'redux'

export interface SettingsStoreState {
  projectUpdated: boolean
  updateSuccess: boolean
  updateError: boolean
  errorMessage: string
}

export const initialState = {
  projectUpdated: false,
  updateSuccess: false,
  updateError: false,
  errorMessage: ''
}

const settings = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case UPDATE_PROJECT_REQUEST:
      return {
        ...state,
        projectUpdated: false
      }
    case UPDATE_PROJECT_SUCCESS:
      return {
        ...state,
        projectUpdated: true,
        updateSuccess: true,
        updateError: false
      }
    case UPDATE_PROJECT_FAILURE:
      return {
        ...state,
        updateError: true,
        updateSuccess: false,
        errorMessage: action.error.data.name[0]
      }
    case CHANGE_VISIBILITY_REQUEST:
      return {
        ...state,
        projectUpdated: false
      }
    case CHANGE_VISIBILITY_SUCCESS:
      return {
        ...state,
        projectUpdated: true,
        updateSuccess: true
      }
    case CHANGE_VISIBILITY_FAILURE:
      return {
        ...state,
        updateError: true
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
    case CLOSE_ERROR:
      return {
        ...state,
        updateError: false
      }
    case CLOSE_SUCCESS:
      return {
        ...state,
        updateSuccess: false,
        projectUpdated: false
      }
    default:
      return state
  }
}

export default settings
