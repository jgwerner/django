import {
  LOGIN_REQUEST,
  LOGIN_SUCCESS,
  LOGIN_FAILURE,
  CLOSE_ERROR
} from './actions'
import { AnyAction } from 'redux'

export interface LoginStoreState {
  accountID: string
  token: string
  loggingIn: boolean
  loginError: boolean
  errorMessage: string
}

export const initialState = {
  accountID: '',
  token: '',
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
        token: action.data.token,
        accountID: action.data.account_id
      }
    case LOGIN_FAILURE:
      return {
        ...state,
        loggingIn: false,
        loginError: true,
        errorMessage: action.error.data.non_field_errors[0]
      }
    case CLOSE_ERROR:
      return {
        ...state,
        loginError: false
      }
    default:
      return state
  }
}

export default login
