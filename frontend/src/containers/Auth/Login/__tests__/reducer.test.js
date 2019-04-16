import reducer from '../reducer'
import * as actions from '../actions'

describe('login reducer', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      accountID: '',
      token: '',
      loggingIn: false,
      loginError: false,
      errorMessage: ''
    })
  })

  it('should handle LOGIN_SUCCESS', () => {
    expect(
      reducer([], {
        type: actions.LOGIN_SUCCESS,
        data: {
          token: 'access token',
          account_id: 'account id'
        }
      })
    ).toEqual({
      token: 'access token',
      accountID: 'account id',
      loggingIn: false
    })
  })
})
