import {
  CHANGE_PASSWORD_REQUEST,
  CHANGE_PASSWORD_SUCCESS,
  CHANGE_PASSWORD_FAILURE,
  UPDATE_PROFILE_REQUEST,
  UPDATE_PROFILE_SUCCESS,
  UPDATE_PROFILE_FAILURE
} from './actions'

const initialState = {}

const account = (state = initialState, action) => {
  switch (action.type) {
    case CHANGE_PASSWORD_REQUEST:
      return {
        ...state
      }

    case CHANGE_PASSWORD_SUCCESS:
      return {
        ...state
      }
    case CHANGE_PASSWORD_FAILURE:
      return {
        ...state
      }
    case UPDATE_PROFILE_REQUEST:
      return {
        ...state
      }
    case UPDATE_PROFILE_SUCCESS:
      return {
        ...state
      }
    case UPDATE_PROFILE_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default account
