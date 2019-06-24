import {
  GET_APPS_REQUEST,
  GET_APPS_SUCCESS,
  GET_APPS_FAILURE,
  NEW_APP_REQUEST,
  NEW_APP_SUCCESS,
  NEW_APP_FAILURE,
  DELETE_APP_REQUEST,
  DELETE_APP_SUCCESS,
  DELETE_APP_FAILURE
} from './actions'
import { AnyAction } from 'redux'

export interface OAuth2StoreState {
  apps: any
  appsFetched: boolean
  newApp: boolean
  appDeleted: boolean
}

export const initialState = {
  apps: [],
  appsFetched: false,
  newApp: false,
  appDeleted: false
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
        newApp: false
      }
    case NEW_APP_SUCCESS:
      return {
        ...state,
        newApp: true
      }
    case NEW_APP_FAILURE:
      return {
        ...state
      }
    case DELETE_APP_REQUEST:
      return {
        ...state,
        appDeleted: false
      }
    case DELETE_APP_SUCCESS:
      return {
        ...state,
        appDeleted: true
      }
    case DELETE_APP_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default oauth2
