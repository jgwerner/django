import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('login reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      accountID: '',
      loggingIn: false,
      loginError: false,
      errorMessage: ''
    })
  })

  it('should handle LOGIN_SUCCESS', () => {
    const successAction = {
      type: actions.LOGIN_SUCCESS,
      data: {
        account_id: 'account id'
      }
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      accountID: 'account id',
      loggingIn: false
    })
  })

  it('should handle LOGIN_FAILURE', () => {
    const failureAction = {
      type: actions.LOGIN_FAILURE,
      error: {
        data: {
          non_field_errors: ['Unable to log in with provided credentials.']
        }
      }
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      loggingIn: false,
      errorMessage: failureAction.error.data.non_field_errors[0],
      loginError: true
    })
  })

  it('should handle CLOSE_ERROR', () => {
    const closeErrorAction = {
      type: actions.CLOSE_ERROR
    }
    expect(reducer(initialState, closeErrorAction)).toEqual({
      ...initialState,
      loginError: false
    })
  })
})
