import {
  LOGIN_REQUEST,
  LOGIN_SUCCESS,
  LOGIN_FAILURE,
  CLOSE_ERROR,
  TOKEN_LOGIN_REQUEST,
  TOKEN_LOGIN_SUCCESS,
  TOKEN_LOGIN_FAILURE
} from './actions'
import { AnyAction } from 'redux'

export interface LoginStoreState {
  accountID: string
  loggingIn: boolean
  loginError: boolean
  errorMessage: string
}

export const initialState = {
  accountID: '',
  loggingIn: false,
  loginError: false,
  errorMessage: ''
}

const login = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case LOGIN_REQUEST:
      return {
        ...state,
        loggingIn: true
      }
    case LOGIN_SUCCESS:
      return {
        ...state,
        loggingIn: false,
        accountID: action.data.account_id
      }
    case LOGIN_FAILURE:
      return {
        ...state,
        loggingIn: false,
        loginError: true,
        errorMessage: action.error.data.non_field_errors
          ? action.error.data.non_field_errors[0]
          : 'Login Failed'
      }
    case CLOSE_ERROR:
      return {
        ...state,
        loginError: false
      }
    case TOKEN_LOGIN_REQUEST:
      return {
        ...state
      }
    case TOKEN_LOGIN_SUCCESS:
      return {
        ...state
      }
    case TOKEN_LOGIN_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default login
