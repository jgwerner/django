import { combineReducers, AnyAction } from 'redux'
import {
  PROJECT_DETAILS_REQUEST,
  PROJECT_DETAILS_SUCCESS,
  PROJECT_DETAILS_FAILURE
} from './actions'
import workspaces, { WorkspacesStoreState } from './ProjectWorkspaces/reducer'
import settings, { SettingsStoreState } from './Settings/reducer'

export interface DetailsStoreState {
  projectDetails: any
  projectFetched: boolean
}

export const initialState = {
  projectDetails: {},
  projectFetched: false
}

export const details = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case PROJECT_DETAILS_REQUEST:
      return {
        ...state,
        projectFetched: false
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

export interface ProjectStoreState {
  details: DetailsStoreState
  workspaces: WorkspacesStoreState
  settings: SettingsStoreState
}

const projectReducer = combineReducers({
  details,
  workspaces,
  settings
})

export default projectReducer
