import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import * as LoginActions from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('home actions', () => {
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
        const request = moxios.requests.mostRecent(values)
        request.respondWith({
          status: 200,
          response: { loginData: ['login data'] }
        })
      })

      const expectedActions = [
        { type: 'LOGIN_REQUEST' },
        { type: 'LOGIN_SUCCESS', data: { loginData: ['login data'] } }
      ]

      const store = mockStore({ loginData: {} })

      return store.dispatch(LoginActions.login(values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
