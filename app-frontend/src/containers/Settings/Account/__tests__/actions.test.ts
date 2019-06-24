import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import {
  changePassword,
  deleteAccount,
  closePasswordSuccess,
  closePasswordError
} from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('account settings actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('change password', () => {
    it('dispatches correct action and payload', () => {
      const accountID = 'account id'
      const values = {
        password: 'new password'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'password changed'
        })
      })

      const expectedActions = [
        { type: 'CHANGE_PASSWORD_REQUEST' },
        {
          type: 'CHANGE_PASSWORD_SUCCESS',
          data: 'password changed'
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(changePassword(accountID, values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const accountID = 'account id'
      const values = {
        password: 'new password'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to change password' }
        })
      })

      const expectedActions = [
        { type: 'CHANGE_PASSWORD_REQUEST' },
        {
          type: 'CHANGE_PASSWORD_FAILURE',
          error: { data: 'unable to change password' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(changePassword(accountID, values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  it('closes password success message', () => {
    const expectedActions = { type: 'CLOSE_PASSWORD_SUCCESS' }
    expect(closePasswordSuccess()).toEqual(expectedActions)
  })

  it('closes password error message', () => {
    const expectedActions = { type: 'CLOSE_PASSWORD_ERROR' }
    expect(closePasswordError()).toEqual(expectedActions)
  })

  describe('delete account', () => {
    it('dispatches correct action and payload', () => {
      const accountID = 'account id'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'account deleted'
        })
      })

      const expectedActions = [
        { type: 'DELETE_ACCOUNT_REQUEST' },
        {
          type: 'DELETE_ACCOUNT_SUCCESS',
          data: 'account deleted'
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(deleteAccount(accountID)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const accountID = 'account id'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to delete account' }
        })
      })

      const expectedActions = [
        { type: 'DELETE_ACCOUNT_REQUEST' },
        {
          type: 'DELETE_ACCOUNT_FAILURE',
          error: { data: 'unable to delete account' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(deleteAccount(accountID)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
