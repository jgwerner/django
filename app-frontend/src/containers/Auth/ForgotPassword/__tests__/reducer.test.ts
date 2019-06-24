import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('forgot password reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      resetPasswordRequest: false,
      confirmPasswordRequest: false,
      confirmPasswordSuccess: false,
      confirmPasswordErrorMsg: ''
    })
  })

  it('should handle RESET_PASSWORD_REQUEST', () => {
    const requestAction = {
      type: actions.RESET_PASSWORD_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState,
      resetPasswordRequest: true
    })
  })

  it('should handle RESET_PASSWORD_SUCCESS', () => {
    const successAction = {
      type: actions.RESET_PASSWORD_SUCCESS
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      resetPasswordRequest: false
    })
  })

  it('should handle RESET_PASSWORD_FAILURE', () => {
    const failureAction = {
      type: actions.RESET_PASSWORD_FAILURE,
      error: {
        data: 'There was an error resetting your password'
      }
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      resetPasswordRequest: false,
      resetPasswordError: true,
      resetPasswordErrorMsg: failureAction.error.data
    })
  })

  it('should handle CONFIRM_PASSWORD_REQUEST', () => {
    const requestAction = {
      type: actions.CONFIRM_PASSWORD_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState,
      confirmPasswordRequest: true
    })
  })

  it('should handle CONFIRM_PASSWORD_SUCCESS', () => {
    const successAction = {
      type: actions.CONFIRM_PASSWORD_SUCCESS
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      confirmPasswordRequest: false,
      confirmPasswordSuccess: true
    })
  })

  it('should handle CONFIRM_PASSWORD_FAILURE', () => {
    const failureAction = {
      type: actions.CONFIRM_PASSWORD_FAILURE,
      error: {
        data: 'There was an error resetting your password'
      }
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      confirmPasswordRequest: false,
      confirmPasswordError: true,
      confirmPasswordErrorMsg: failureAction.error.data
    })
  })
})
