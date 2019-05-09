import {
  CHANGE_PASSWORD_REQUEST,
  CHANGE_PASSWORD_SUCCESS,
  CHANGE_PASSWORD_FAILURE,
  UPDATE_PROFILE_REQUEST,
  UPDATE_PROFILE_SUCCESS,
  UPDATE_PROFILE_FAILURE,
  CLOSE_PROFILE_SUCCESS,
  CLOSE_PROFILE_ERROR,
  CLOSE_PASSWORD_SUCCESS,
  CLOSE_PASSWORD_ERROR,
  AccountSettingsActions
} from './actions'

export interface AccountSettingsStoreState {
  profileUpdateSuccess: boolean
  profileUpdateError: boolean
  passwordUpdateSuccess: boolean
  passwordUpdateError: boolean
}

const initialState = {
  profileUpdateSuccess: false,
  profileUpdateError: false,
  passwordUpdateSuccess: false,
  passwordUpdateError: false
}

const account = (state = initialState, action: AccountSettingsActions) => {
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
    case UPDATE_PROFILE_REQUEST:
      return {
        ...state,
        profileUpdateSuccess: false,
        profileUpdateError: false
      }
    case UPDATE_PROFILE_SUCCESS:
      return {
        ...state,
        profileUpdateSuccess: true
      }
    case UPDATE_PROFILE_FAILURE:
      return {
        ...state,
        profileUpdateError: true
      }
    case CLOSE_PROFILE_SUCCESS:
      return {
        ...state,
        profileUpdateSuccess: false
      }
    case CLOSE_PROFILE_ERROR:
      return {
        ...state,
        profileUpdateError: false
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
