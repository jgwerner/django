import settings, { initialState } from '../reducer'
import * as actions from '../actions'

describe('project reducer', () => {
  it('should return the initial state', () => {
    expect(settings(initialState, { type: null })).toEqual({
      projectUpdated: false,
      updateSuccess: false,
      updateError: false,
      errorMessage: ''
    })
  })

  it('should handle UPDATE_PROJECT_REQUEST', () => {
    const requestAction = {
      type: actions.UPDATE_PROJECT_REQUEST
    }
    expect(settings(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle UPDATE_PROJECT_SUCCESS', () => {
    const successAction = {
      type: actions.UPDATE_PROJECT_SUCCESS
    }
    expect(settings(initialState, successAction)).toEqual({
      ...initialState,
      projectUpdated: true,
      updateSuccess: true,
      updateError: false
    })
  })

  it('should handle UPDATE_PROJECT_FAILURE', () => {
    const failureAction = {
      type: actions.UPDATE_PROJECT_FAILURE,
      error: {
        data: {
          name: ['You can have only one project named project']
        }
      }
    }
    expect(settings(initialState, failureAction)).toEqual({
      ...initialState,
      updateError: true,
      errorMessage: failureAction.error.data.name[0],
      updateSuccess: false
    })
  })

  it('should handle CHANGE_VISIBILITY_REQUEST', () => {
    const requestAction = {
      type: actions.CHANGE_VISIBILITY_REQUEST
    }
    expect(settings(initialState, requestAction)).toEqual({
      ...initialState,
      projectUpdated: false
    })
  })

  it('should handle CHANGE_VISIBILITY_SUCCESS', () => {
    const successAction = {
      type: actions.CHANGE_VISIBILITY_SUCCESS
    }
    expect(settings(initialState, successAction)).toEqual({
      ...initialState,
      projectUpdated: true,
      updateSuccess: true
    })
  })

  it('should handle CHANGE_VISIBILITY_FAILURE', () => {
    const failureAction = {
      type: actions.CHANGE_VISIBILITY_FAILURE
    }
    expect(settings(initialState, failureAction)).toEqual({
      ...initialState,
      updateError: true
    })
  })

  it('should handle DELETE_PROJECT_REQUEST', () => {
    const requestAction = {
      type: actions.DELETE_PROJECT_REQUEST
    }
    expect(settings(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle DELETE_PROJECT_SUCCESS', () => {
    const successAction = {
      type: actions.DELETE_PROJECT_SUCCESS
    }
    expect(settings(initialState, successAction)).toEqual({
      ...initialState
    })
  })

  it('should handle DELETE_PROJECT_FAILURE', () => {
    const failureAction = {
      type: actions.DELETE_PROJECT_FAILURE
    }
    expect(settings(initialState, failureAction)).toEqual({
      ...initialState
    })
  })
})
