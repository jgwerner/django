import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('account settings reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      passwordUpdateSuccess: false,
      passwordUpdateError: false
    })
  })

  it('should handle CHANGE_PASSWORD_REQUEST', () => {
    const requestAction = {
      type: actions.CHANGE_PASSWORD_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState,
      passwordUpdateSuccess: false,
      passwordUpdateError: false
    })
  })

  it('should handle CHANGE_PASSWORD_SUCCESS', () => {
    const successAction = {
      type: actions.CHANGE_PASSWORD_SUCCESS
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      passwordUpdateSuccess: true
    })
  })

  it('should handle CHANGE_PASSWORD_FAILURE', () => {
    const failureAction = {
      type: actions.CHANGE_PASSWORD_FAILURE
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState,
      passwordUpdateError: true
    })
  })
  it('should handle CLOSE_PASSWORD_SUCCESS', () => {
    const closeBannerAction = {
      type: actions.CLOSE_PASSWORD_SUCCESS
    }
    expect(reducer(initialState, closeBannerAction)).toEqual({
      ...initialState,
      passwordUpdateSuccess: false
    })
  })

  it('should handle CLOSE_PASSWORD_ERROR', () => {
    const closeBannerAction = {
      type: actions.CLOSE_PASSWORD_ERROR
    }
    expect(reducer(initialState, closeBannerAction)).toEqual({
      ...initialState,
      passwordUpdateError: false
    })
  })
})
