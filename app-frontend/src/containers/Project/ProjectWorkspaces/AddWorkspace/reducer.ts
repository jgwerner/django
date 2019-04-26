import {
  ADD_WORKSPACE_REQUEST,
  ADD_WORKSPACE_SUCCESS,
  ADD_WORKSPACE_FAILURE
} from './actions'
import { AnyAction } from 'redux'

export interface AddWorkspaceStoreState {
  newWorkspace: boolean
}

const initialState = {
  newWorkspace: false
}

const add = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case ADD_WORKSPACE_REQUEST:
      return {
        ...state,
        newWorkspace: false
      }
    case ADD_WORKSPACE_SUCCESS:
      return {
        ...state,
        newWorkspace: true
      }
    case ADD_WORKSPACE_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default add
