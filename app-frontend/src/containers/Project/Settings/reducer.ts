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
  CLOSE_UPDATE_ERROR,
  CLOSE_UPDATE_SUCCESS,
  CLOSE_DELETE_SUCCESS,
  CLOSE_DELETE_ERROR
} from './actions'
import { AnyAction } from 'redux'

export interface SettingsStoreState {
  projectUpdated: boolean
  updateProjectSuccess: boolean
  updateProjectError: boolean
  updateProjectErrorMessage: string
  deleteProjectSuccess: boolean
  deleteProjectError: boolean
}

export const initialState = {
  projectUpdated: false,
  updateProjectSuccess: false,
  updateProjectError: false,
  updateProjectErrorMessage: '',
  deleteProjectSuccess: false,
  deleteProjectError: false
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
        updateProjectSuccess: true,
        updateProjectError: false
      }
    case UPDATE_PROJECT_FAILURE:
      return {
        ...state,
        updateProjectError: true,
        updateProjectSuccess: false,
        updateProjectErrorMessage: action.error.data.name
          ? action.error.data.name[0]
          : 'Error updating project'
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
        updateProjectSuccess: true
      }
    case CHANGE_VISIBILITY_FAILURE:
      return {
        ...state,
        updateProjectError: true
      }
    case DELETE_PROJECT_REQUEST:
      return {
        ...state
      }
    case DELETE_PROJECT_SUCCESS:
      return {
        ...state,
        deleteProjectSuccess: true
      }
    case DELETE_PROJECT_FAILURE:
      return {
        ...state,
        deleteProjectError: true
      }
    case CLOSE_UPDATE_ERROR:
      return {
        ...state,
        updateProjectError: false
      }
    case CLOSE_UPDATE_SUCCESS:
      return {
        ...state,
        updateProjectSuccess: false,
        projectUpdated: false
      }
    case CLOSE_DELETE_ERROR:
      return {
        ...state,
        deleteProjectError: false
      }
    case CLOSE_DELETE_SUCCESS:
      return {
        ...state,
        deleteProjectSuccess: false
      }
    default:
      return state
  }
}

export default settings
