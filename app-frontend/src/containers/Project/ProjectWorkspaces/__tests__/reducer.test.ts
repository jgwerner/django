import { servers, initialState } from '../reducer'
import * as actions from '../actions'

describe('project reducer', () => {
  it('should return the initial state', () => {
    expect(servers(initialState, { type: null })).toEqual({
      serverSizes: [],
      workspaces: [],
      serverRunning: false,
      deleteServerSuccess: false,
      deleteServerError: false,
      serverStatus: '',
      startServerError: false
    })
  })

  it('should handle GET_SIZES_REQUEST', () => {
    const requestAction = {
      type: actions.GET_SIZES_REQUEST
    }
    expect(servers(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle GET_SIZES_SUCCESS', () => {
    const successAction = {
      type: actions.GET_SIZES_SUCCESS,
      data: ['server size options']
    }
    expect(servers(initialState, successAction)).toEqual({
      ...initialState,
      serverSizes: successAction.data
    })
  })

  it('should handle GET_SIZES_FAILURE', () => {
    const failureAction = {
      type: actions.GET_SIZES_FAILURE
    }
    expect(servers(initialState, failureAction)).toEqual({
      ...initialState
    })
  })

  it('should handle GET_WORKSPACES_REQUEST', () => {
    const requestAction = {
      type: actions.GET_WORKSPACES_REQUEST
    }
    expect(servers(initialState, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle GET_WORKSPACES_SUCCESS', () => {
    const successAction = {
      type: actions.GET_WORKSPACES_SUCCESS,
      data: ['workspaces']
    }
    expect(servers(initialState, successAction)).toEqual({
      ...initialState,
      workspaces: successAction.data
    })
  })

  it('should handle GET_WORKSPACES_FAILURE', () => {
    const failureAction = {
      type: actions.GET_WORKSPACES_FAILURE
    }
    expect(servers(initialState, failureAction)).toEqual({
      ...initialState
    })
  })

  it('should handle START_SERVER_REQUEST', () => {
    const requestAction = {
      type: actions.START_SERVER_REQUEST
    }
    expect(servers(initialState, requestAction)).toEqual({
      ...initialState,
      serverRunning: false
    })
  })

  it('should handle START_SERVER_SUCCESS', () => {
    const successAction = {
      type: actions.START_SERVER_SUCCESS
    }
    expect(servers(initialState, successAction)).toEqual({
      ...initialState,
      serverRunning: true
    })
  })

  it('should handle START_SERVER_FAILURE', () => {
    const failureAction = {
      type: actions.START_SERVER_FAILURE
    }
    expect(servers(initialState, failureAction)).toEqual({
      ...initialState,
      startServerError: true
    })
  })

  it('should handle STOP_SERVER_REQUEST', () => {
    const requestAction = {
      type: actions.STOP_SERVER_REQUEST
    }
    expect(servers(initialState, requestAction)).toEqual({
      ...initialState,
      serverRunning: true
    })
  })

  it('should handle STOP_SERVER_SUCCESS', () => {
    const successAction = {
      type: actions.STOP_SERVER_SUCCESS
    }
    expect(servers(initialState, successAction)).toEqual({
      ...initialState,
      serverRunning: false
    })
  })

  it('should handle STOP_SERVER_FAILURE', () => {
    const failureAction = {
      type: actions.STOP_SERVER_FAILURE
    }
    expect(servers(initialState, failureAction)).toEqual({
      ...initialState
    })
  })

  it('should handle DELETE_SERVER_REQUEST', () => {
    const requestAction = {
      type: actions.DELETE_SERVER_REQUEST
    }
    expect(servers(initialState, requestAction)).toEqual({
      ...initialState,
      deleteServerSuccess: false,
      deleteServerError: false
    })
  })

  it('should handle DELETE_SERVER_SUCCESS', () => {
    const successAction = {
      type: actions.DELETE_SERVER_SUCCESS
    }
    expect(servers(initialState, successAction)).toEqual({
      ...initialState,
      deleteServerSuccess: true
    })
  })

  it('should handle DELETE_SERVER_FAILURE', () => {
    const failureAction = {
      type: actions.DELETE_SERVER_FAILURE
    }
    expect(servers(initialState, failureAction)).toEqual({
      ...initialState,
      deleteServerError: true
    })
  })

  it('should handle UPDATE_STATUS', () => {
    const expectedAction = {
      type: actions.UPDATE_STATUS,
      data: 'current status'
    }
    let currentWorkspace = { status: 'current workspace' }
    currentWorkspace.status = 'current status'
    expect(servers(initialState, expectedAction)).toEqual({
      ...initialState,
      workspaces: [currentWorkspace]
    })
  })
})
