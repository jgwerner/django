import history from 'utils/history'
import UpdateProjectAPI from './api'

export const UPDATE_PROJECT_REQUEST = 'UPDATE_PROJECT_REQUEST'
export const UPDATE_PROJECT_SUCCESS = 'UPDATE_PROJECT_SUCCESS'
export const UPDATE_PROJECT_FAILURE = 'UPDATE_PROJECT_FAILURE'
export const CHANGE_VISIBILITY_REQUEST = 'CHANGE_VISIBILITY_REQUEST'
export const CHANGE_VISIBILITY_SUCCESS = 'CHANGE_VISIBILITY_SUCCESS'
export const CHANGE_VISIBILITY_FAILURE = 'CHANGE_VISIBILITY_FAILURE'
export const DELETE_PROJECT_REQUEST = 'DELETE_PROJECT_REQUEST'
export const DELETE_PROJECT_SUCCESS = 'DELETE_PROJECT_SUCCESS'
export const DELETE_PROJECT_FAILURE = 'DELETE_PROJECT_FAILURE'
export const SEARCH_RESULTS_REQUEST = 'GET_SEARCH_RESULTS_REQUEST'
export const SEARCH_RESULTS_SUCCESS = 'GET_SEARCH_RESULTS_SUCCESS'
export const SEARCH_RESULTS_FAILURE = 'GET_SEARCH_RESULTS_FAILURE'

export const updateProject = (username, projectID, values) => dispatch => {
  function request() {
    return {
      type: UPDATE_PROJECT_REQUEST
    }
  }
  function success(data) {
    return {
      type: UPDATE_PROJECT_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: UPDATE_PROJECT_FAILURE
    }
  }
  dispatch(request())
  return UpdateProjectAPI.updateDetails(username, projectID, values).then(
    data => {
      dispatch(success(data))
      history.push(`/${username}/${values.name}/settings`)
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const changeVisibility = (
  username,
  projectName,
  visibility
) => dispatch => {
  function request() {
    return {
      type: CHANGE_VISIBILITY_REQUEST
    }
  }
  function success(data) {
    return {
      type: CHANGE_VISIBILITY_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: CHANGE_VISIBILITY_FAILURE
    }
  }
  dispatch(request())
  return UpdateProjectAPI.changeVisibility(
    username,
    projectName,
    visibility
  ).then(
    data => {
      dispatch(success(data))
      history.goBack()
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const deleteProject = (username, projectName) => dispatch => {
  function request() {
    return {
      type: DELETE_PROJECT_REQUEST
    }
  }
  function success(data) {
    return {
      type: DELETE_PROJECT_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: DELETE_PROJECT_FAILURE
    }
  }
  dispatch(request())
  return UpdateProjectAPI.deleteProject(username, projectName).then(
    data => {
      dispatch(success(data))
      history.push('/')
    },
    error => {
      dispatch(failure(error))
    }
  )
}

export const getSearchResults = (username, value) => dispatch => {
  function request() {
    return {
      type: SEARCH_RESULTS_REQUEST
    }
  }
  function success(data) {
    return {
      type: SEARCH_RESULTS_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: SEARCH_RESULTS_FAILURE
    }
  }
  dispatch(request())
  return UpdateProjectAPI.getSearchResults(username, value).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
