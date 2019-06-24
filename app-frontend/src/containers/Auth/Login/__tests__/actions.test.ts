import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { login } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('login actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('login', () => {
    it('dispatches correct action and payload', () => {
      const values = {
        username: 'username',
        password: 'password'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { loginData: ['login data'] }
        })
      })

      const expectedActions = [
        { type: 'LOGIN_REQUEST' },
        { type: 'LOGIN_SUCCESS', data: { loginData: ['login data'] } }
      ]

      const store = mockStore({})

      return store.dispatch<any>(login(values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const values = {
        username: 'username',
        password: 'password'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to login' }
        })
      })

      const expectedActions = [
        { type: 'LOGIN_REQUEST' },
        { type: 'LOGIN_FAILURE', error: { data: 'unable to login' } }
      ]

      const store = mockStore({})

      return store.dispatch<any>(login(values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
