import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('project list reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      projects: [],
      projectsFetched: false
    })
  })

  it('should handle PROJECT_LIST_REQUEST', () => {
    const requestAction = {
      type: actions.PROJECT_LIST_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle PROJECT_LIST_SUCCESS', () => {
    const successAction = {
      type: actions.PROJECT_LIST_SUCCESS,
      data: ['list of projects']
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      projects: ['list of projects'],
      projectsFetched: true
    })
  })

  it('should handle PROJECT_LIST_FAILURE', () => {
    const failureAction = {
      type: actions.PROJECT_LIST_FAILURE
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState
    })
  })
})
