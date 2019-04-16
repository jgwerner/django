import {
  PROJECT_LIST_REQUEST,
  PROJECT_LIST_SUCCESS,
  PROJECT_LIST_FAILURE
} from './actions'

const initialState = {
  projects: [],
  projectsFetched: false
}

const projects = (state = initialState, action) => {
  switch (action.type) {
    case PROJECT_LIST_REQUEST:
      return {
        ...state
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
