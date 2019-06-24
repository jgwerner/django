import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { resetPassword, resetPasswordConfirm } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('reset password actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('reset password email request', () => {
    it('dispatches correct action and payload', () => {
      const values = {
        email: 'email'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200
        })
      })

      const expectedActions = [
        { type: 'RESET_PASSWORD_REQUEST' },
        { type: 'RESET_PASSWORD_SUCCESS' }
      ]

      const store = mockStore({})

      return store.dispatch<any>(resetPassword(values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const values = {
        email: 'email'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'error resetting password' }
        })
      })

      const expectedActions = [
        { type: 'RESET_PASSWORD_REQUEST' },
        {
          type: 'RESET_PASSWORD_FAILURE',
          error: { data: 'error resetting password' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(resetPassword(values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  describe('reset password confirm', () => {
    it('dispatches correct action and payload', () => {
      const values = {
        password: 'password'
      }
      const params = {
        uid: 'uid',
        token: 'token'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200
        })
      })

      const expectedActions = [
        { type: 'CONFIRM_PASSWORD_REQUEST' },
        { type: 'CONFIRM_PASSWORD_SUCCESS' }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(resetPasswordConfirm(params, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      const values = {
        password: 'password'
      }
      const params = {
        uid: 'uid',
        token: 'token'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'error resetting password' }
        })
      })

      const expectedActions = [
        { type: 'CONFIRM_PASSWORD_REQUEST' },
        {
          type: 'CONFIRM_PASSWORD_FAILURE',
          error: { data: 'error resetting password' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(resetPasswordConfirm(params, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })
})
