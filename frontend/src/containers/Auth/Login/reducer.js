import { LOGIN_REQUEST, LOGIN_SUCCESS, LOGIN_FAILURE } from './actions'

const initialState = {
  accountID: '',
  token: '',
  loggingIn: false,
  loginError: false,
  errorMessage: ''
}

const login = (state = initialState, action) => {
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
        errorMessage: action.error
      }
    default:
      return state
  }
}

export default login
