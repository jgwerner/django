import add, { initialState } from '../reducer'
import * as actions from '../actions'

describe('add project reducer', () => {
  it('should return the initial state', () => {
    expect(add(initialState, { type: null })).toEqual({
      newWorkspace: false
    })
  })

  it('should handle ADD_WORKSPACE_REQUEST', () => {
    const requestAction = {
      type: actions.ADD_WORKSPACE_REQUEST
    }
    expect(add(initialState, requestAction)).toEqual({
      ...initialState,
      newWorkspace: false
    })
  })

  it('should handle ADD_WORKSPACE_SUCCESS', () => {
    const requestAction = {
      type: actions.ADD_WORKSPACE_SUCCESS
    }
    expect(add(initialState, requestAction)).toEqual({
      ...initialState,
      newWorkspace: true
    })
  })

  it('should handle ADD_WORKSPACE_FAILURE', () => {
    const failureAction = {
      type: actions.ADD_WORKSPACE_FAILURE
    }
    expect(add(initialState, failureAction)).toEqual({
      ...initialState
    })
  })
})
