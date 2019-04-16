import history from 'utils/history'
import AddProjectAPI from './api'

export const ADD_PROJECT_REQUEST = 'ADD_PROJECT_REQUEST'
export const ADD_PROJECT_SUCCESS = 'ADD_PROJECT_SUCCESS'
export const ADD_PROJECT_FAILURE = 'ADD_PROJECT_FAILURE'

export const addProject = (username, values) => dispatch => {
  function request() {
    return {
      type: ADD_PROJECT_REQUEST
    }
  }
  function success(data) {
    return {
      type: ADD_PROJECT_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: ADD_PROJECT_FAILURE
    }
  }
  dispatch(request())
  return AddProjectAPI.addProject(username, values).then(
    data => {
      dispatch(success(data))
      history.push('/')
    },
    error => {
      dispatch(failure(error))
    }
  )
}
