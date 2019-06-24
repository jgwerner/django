import { details, initialState } from '../reducer'
import * as actions from '../actions'

describe('project reducer', () => {
  it('should return the initial state', () => {
    expect(details(initialState, { type: null })).toEqual({
      projectDetails: {},
      projectFetched: false
    })
  })

  it('should handle PROJECT_DETAILS_REQUEST', () => {
    const requestAction = {
      type: actions.PROJECT_DETAILS_REQUEST
    }
    expect(details(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle PROJECT_DETAILS_SUCCESS', () => {
    const successAction = {
      type: actions.PROJECT_DETAILS_SUCCESS,
      data: ['project details']
    }
    expect(details(initialState, successAction)).toEqual({
      ...initialState,
      projectDetails: successAction.data[0],
      projectFetched: true
    })
  })

  it('should handle PROJECT_DETAILS_FAILURE', () => {
    const failureAction = {
      type: actions.PROJECT_DETAILS_FAILURE
    }
    expect(details(initialState, failureAction)).toEqual({
      ...initialState
    })
  })
})
