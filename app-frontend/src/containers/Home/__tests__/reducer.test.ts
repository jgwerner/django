import { user, initialState } from '../reducer'
import * as actions from '../actions'
import { TOKEN_LOGIN_SUCCESS } from '../../Auth/Login/actions'

describe('add project reducer', () => {
  it('should return the initial state', () => {
    expect(user(initialState as any, { type: null })).toEqual({
      accountID: '',
      username: '',
      firstName: '',
      lastName: '',
      email: '',
      profileInfo: {},
      profileInfoFetched: false
    })
  })

  it('should handle TOKEN_LOGIN_SUCCESS', () => {
    const requestAction = {
      type: TOKEN_LOGIN_SUCCESS
    }
    expect(user(initialState as any, requestAction)).toEqual({
      ...initialState,
      profileInfoFetched: false
    })
  })

  it('should handle USER_INFO_REQUEST', () => {
    const requestAction = {
      type: actions.USER_INFO_REQUEST
    }
    expect(user(initialState as any, requestAction)).toEqual({
      ...initialState
    })
  })

  it('should handle USER_INFO_SUCCESS', () => {
    const successAction = {
      type: actions.USER_INFO_SUCCESS,
      data: {
        id: 'account id',
        username: 'username',
        first_name: 'first name',
        last_name: 'last name',
        email: 'email',
        profile: { 'profile info': 'info' }
      }
    }
    expect(user(initialState as any, successAction)).toEqual({
      ...initialState,
      accountID: successAction.data.id,
      username: successAction.data.username,
      firstName: successAction.data.first_name,
      lastName: successAction.data.last_name,
      email: successAction.data.email,
      profileInfo: successAction.data.profile,
      profileInfoFetched: true
    })
  })

  it('should handle USER_INFO_FAILURE', () => {
    const failureAction = {
      type: actions.USER_INFO_FAILURE
    }
    expect(user(initialState as any, failureAction)).toEqual({
      ...initialState
    })
  })

  it('should handle LOGOUT', () => {
    const logoutAction = {
      type: actions.LOGOUT
    }
    expect(user(initialState as any, logoutAction)).toEqual({
      ...initialState
    })
  })
})
