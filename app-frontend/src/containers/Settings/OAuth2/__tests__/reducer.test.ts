import reducer, { initialState } from '../reducer'
import * as actions from '../actions'

describe('OAuth2 settings reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(initialState, { type: null })).toEqual({
      apps: [],
      appsFetched: false,
      createAppSuccess: false,
      deleteAppSuccess: false,
      createAppError: false,
      deleteAppError: false
    })
  })

  it('should handle GET_APPS_REQUEST', () => {
    const requestAction = {
      type: actions.GET_APPS_REQUEST
    }
    expect(reducer(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle CHANGE_PASSWORD_SUCCESS', () => {
    const successAction = {
      type: actions.GET_APPS_SUCCESS,
      data: ['list of apps']
    }
    expect(reducer(initialState, successAction)).toEqual({
      ...initialState,
      apps: successAction.data,
      appsFetched: true
    })
  })

  it('should handle GET_APPS_FAILURE', () => {
    const failureAction = {
      type: actions.GET_APPS_FAILURE
    }
    expect(reducer(initialState, failureAction)).toEqual({
      ...initialState
    })
  })
  it('should handle NEW_APP_REQUEST', () => {
    const expectedAction = {
      type: actions.NEW_APP_REQUEST
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      createAppSuccess: false,
      createAppError: false
    })
  })

  it('should handle NEW_APP_SUCCESS', () => {
    const expectedAction = {
      type: actions.NEW_APP_SUCCESS
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      createAppSuccess: true
    })
  })

  it('should handle NEW_APP_FAILURE', () => {
    const expectedAction = {
      type: actions.NEW_APP_FAILURE
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      createAppError: true
    })
  })

  it('should handle DELETE_APP_REQUEST', () => {
    const expectedAction = {
      type: actions.DELETE_APP_REQUEST
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      deleteAppSuccess: false,
      deleteAppError: false
    })
  })

  it('should handle DELETE_APP_SUCCESS', () => {
    const expectedAction = {
      type: actions.DELETE_APP_SUCCESS
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      deleteAppSuccess: true
    })
  })

  it('should handle DELETE_APP_FAILURE', () => {
    const expectedAction = {
      type: actions.DELETE_APP_FAILURE
    }
    expect(reducer(initialState, expectedAction)).toEqual({
      ...initialState,
      deleteAppError: true
    })
  })
})
