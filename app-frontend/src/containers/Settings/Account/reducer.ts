import {
  CHANGE_PASSWORD_REQUEST,
  CHANGE_PASSWORD_SUCCESS,
  CHANGE_PASSWORD_FAILURE,
  CLOSE_PASSWORD_SUCCESS,
  CLOSE_PASSWORD_ERROR
} from './actions'
import { AnyAction } from 'redux'

export interface AccountSettingsStoreState {
  passwordUpdateSuccess: boolean
  passwordUpdateError: boolean
}

export const initialState = {
  passwordUpdateSuccess: false,
  passwordUpdateError: false
}

const account = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case CHANGE_PASSWORD_REQUEST:
      return {
        ...state,
        passwordUpdateSuccess: false,
        passwordUpdateError: false
      }
    case CHANGE_PASSWORD_SUCCESS:
      return {
        ...state,
        passwordUpdateSuccess: true
      }
    case CHANGE_PASSWORD_FAILURE:
      return {
        ...state,
        passwordUpdateError: true
      }
    case CLOSE_PASSWORD_SUCCESS:
      return {
        ...state,
        passwordUpdateSuccess: false
      }
    case CLOSE_PASSWORD_ERROR:
      return {
        ...state,
        passwordUpdateError: false
      }
    default:
      return state
  }
}

export default account
