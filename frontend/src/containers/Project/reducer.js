import { combineReducers } from 'redux'
import {
  PROJECT_DETAILS_REQUEST,
  PROJECT_DETAILS_SUCCESS,
  PROJECT_DETAILS_FAILURE
} from './actions'
import workspaces from './Workspaces/reducer'
import settings from './Settings/reducer'

const initialState = {
  projectDetails: {},
  projectFetched: false
}

const details = (state = initialState, action) => {
  switch (action.type) {
    case PROJECT_DETAILS_REQUEST:
      return {
        ...state
      }

    case PROJECT_DETAILS_SUCCESS:
      return {
        ...state,
        projectDetails: action.data[0],
        projectFetched: true
      }
    case PROJECT_DETAILS_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

const projectReducer = combineReducers({
  details,
  workspaces,
  settings
})

export default projectReducer
