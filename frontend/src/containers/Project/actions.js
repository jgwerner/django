import ProjectAPI from './api'

export const PROJECT_DETAILS_REQUEST = 'PROJECT_DETAILS_REQUEST'
export const PROJECT_DETAILS_SUCCESS = 'PROJECT_DETAILS_SUCCESS'
export const PROJECT_DETAILS_FAILURE = 'PROJECT_DETAILS_FAILURE'

export const getProject = (username, projectName) => dispatch => {
  function request() {
    return {
      type: PROJECT_DETAILS_REQUEST
    }
  }
  function success(data) {
    return {
      type: PROJECT_DETAILS_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: PROJECT_DETAILS_FAILURE
    }
  }
  dispatch(request())
  return ProjectAPI.getProject(username, projectName).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
