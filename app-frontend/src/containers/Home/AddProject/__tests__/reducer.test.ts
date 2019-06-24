import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('add project reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      newProjectSuccess: false,
      newProjectError: false
    })
  })

  it('should handle ADD_PROJECT_REQUEST', () => {
    const requestAction = {
      type: actions.ADD_PROJECT_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle ADD_PROJECT_SUCCESS', () => {
    const successAction = {
      type: actions.ADD_PROJECT_SUCCESS
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      newProjectSuccess: true
    })
  })

  it('should handle ADD_PROJECT_FAILURE', () => {
    const failureAction = {
      type: actions.ADD_PROJECT_FAILURE
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      newProjectError: true
    })
  })

  it('should handle CLOSE_ERROR', () => {
    const closeErrorAction = {
      type: actions.CLOSE_ERROR
    }
    expect(reducer(initialState, closeErrorAction)).toEqual({
      ...initialState,
      newProjectError: false
    })
  })
})
