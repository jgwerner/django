import {
  GET_APPS_REQUEST,
  GET_APPS_SUCCESS,
  GET_APPS_FAILURE,
  NEW_APP_REQUEST,
  NEW_APP_SUCCESS,
  NEW_APP_FAILURE,
  DELETE_APP_REQUEST,
  DELETE_APP_SUCCESS,
  DELETE_APP_FAILURE,
  CLOSE_DELETE_SUCCESS,
  CLOSE_CREATE_SUCCESS,
  CLOSE_CREATE_ERROR,
  CLOSE_DELETE_ERROR
} from './actions'
import { AnyAction } from 'redux'

export interface OAuth2StoreState {
  apps: any
  appsFetched: boolean
  createAppSuccess: boolean
  deleteAppSuccess: boolean
  createAppError: boolean
  deleteAppError: boolean
}

export const initialState = {
  apps: [],
  appsFetched: false,
  createAppSuccess: false,
  deleteAppSuccess: false,
  createAppError: false,
  deleteAppError: false
}

const oauth2 = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case GET_APPS_REQUEST:
      return {
        ...state
      }
    case GET_APPS_SUCCESS:
      return {
        ...state,
        apps: action.data,
        appsFetched: true
      }
    case GET_APPS_FAILURE:
      return {
        ...state
      }
    case NEW_APP_REQUEST:
      return {
        ...state,
        createAppSuccess: false,
        createAppError: false
      }
    case NEW_APP_SUCCESS:
      return {
        ...state,
        createAppSuccess: true
      }
    case NEW_APP_FAILURE:
      return {
        ...state,
        createAppError: true
      }
    case DELETE_APP_REQUEST:
      return {
        ...state,
        deleteAppSuccess: false,
        deleteAppError: false
      }
    case DELETE_APP_SUCCESS:
      return {
        ...state,
        deleteAppSuccess: true
      }
    case DELETE_APP_FAILURE:
      return {
        ...state,
        deleteAppError: true
      }
    case CLOSE_DELETE_SUCCESS:
      return {
        ...state,
        deleteAppSuccess: false
      }
    case CLOSE_DELETE_ERROR:
      return {
        ...state,
        deleteAppError: false
      }
    case CLOSE_CREATE_SUCCESS:
      return {
        ...state,
        createAppSuccess: false
      }
    case CLOSE_CREATE_ERROR:
      return {
        ...state,
        createAppError: false
      }
    default:
      return state
  }
}

export default oauth2
