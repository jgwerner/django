import ProjectListAPI from './api'

export const PROJECT_LIST_REQUEST = 'PROJECT_LIST_REQUEST'
export const PROJECT_LIST_SUCCESS = 'PROKECT_LIST_SUCCESS'
export const PROJECT_LIST_FAILURE = 'PROJECT_LIST_FAILURE'

export const getProjectList = username => dispatch => {
  function request() {
    return {
      type: PROJECT_LIST_REQUEST
    }
  }
  function success(data) {
    return {
      type: PROJECT_LIST_SUCCESS,
      data
    }
  }
  function failure() {
    return {
      type: PROJECT_LIST_FAILURE
    }
  }
  dispatch(request())
  return ProjectListAPI.getProjectList(username).then(
    data => {
      dispatch(success(data))
    },
    error => {
      dispatch(failure(error))
    }
  )
}
