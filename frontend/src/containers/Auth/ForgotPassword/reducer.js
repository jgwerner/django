import {
  RESET_PASSWORD_REQUEST,
  RESET_PASSWORD_SUCCESS,
  RESET_PASSWORD_FAILURE,
  CONFIRM_PASSWORD_REQUEST,
  CONFIRM_PASSWORD_SUCCESS,
  CONFIRM_PASSWORD_FAILURE
} from './actions'

const initialState = {
  resetPasswordRequest: false,
  confirmPasswordRequest: false,
  confirmPasswordSuccess: false,
  confirmPasswordErrorMsg: {}
}

const password = (state = initialState, action) => {
  switch (action.type) {
    case RESET_PASSWORD_REQUEST:
      return {
        ...state,
        resetPasswordRequest: true
      }
    case RESET_PASSWORD_SUCCESS:
      return {
        ...state,
        resetPasswordRequest: false
      }
    case RESET_PASSWORD_FAILURE:
      return {
        ...state,
        resetPasswordRequest: false,
        resetPasswordError: true,
        resetPasswordErrorMsg: action.error.data
      }
    case CONFIRM_PASSWORD_REQUEST:
      return {
        ...state,
        confirmPasswordRequest: true
      }
    case CONFIRM_PASSWORD_SUCCESS:
      return {
        ...state,
        confirmPasswordRequest: false,
        confirmPasswordSuccess: true
      }
    case CONFIRM_PASSWORD_FAILURE:
      return {
        ...state,
        confirmPasswordRequest: false,
        confirmPasswordError: true,
        confirmPasswordErrorMsg: action.error.data
      }
    default:
      return state
  }
}

export default password
