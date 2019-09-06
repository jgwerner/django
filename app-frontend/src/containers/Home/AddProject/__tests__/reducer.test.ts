import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('add project reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      createProjectSuccess: false,
      createProjectError: false,
      createProjectErrorMessage: ''
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
      createProjectSuccess: true
    })
  })

  it('should handle ADD_PROJECT_FAILURE', () => {
    const failureAction = {
      type: actions.ADD_PROJECT_FAILURE,
      error: {
        data: {
          name: ['Project with name already exists']
        }
      }
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      createProjectError: true,
      createProjectErrorMessage: 'Project with name already exists'
    })
  })

  it('should handle CLOSE_ERROR', () => {
    const closeErrorAction = {
      type: actions.CLOSE_ERROR
    }
    expect(reducer(initialState, closeErrorAction)).toEqual({
      ...initialState,
      createProjectError: false
    })
  })
})
