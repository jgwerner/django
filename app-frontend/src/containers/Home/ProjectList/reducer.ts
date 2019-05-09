import {
  PROJECT_LIST_REQUEST,
  PROJECT_LIST_SUCCESS,
  PROJECT_LIST_FAILURE
} from './actions'
import { AnyAction } from 'redux'

export interface ProjectListProps {
  projects: any
  projectsFetched: boolean
}

const initialState = {
  projects: [],
  projectsFetched: false
}

const projects = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case PROJECT_LIST_REQUEST:
      return {
        ...state,
        projects: []
      }
    case PROJECT_LIST_SUCCESS:
      return {
        ...state,
        projects: action.data,
        projectsFetched: true
      }
    case PROJECT_LIST_FAILURE:
      return {
        ...state
      }
    default:
      return state
  }
}

export default projects
