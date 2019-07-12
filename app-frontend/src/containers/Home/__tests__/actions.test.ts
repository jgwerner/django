import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { getUserInfo, logout } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('home page actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('get user info', () => {
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: {
            userInfo: {
              accountID: 'account id',
              username: 'username',
              firstName: 'first name',
              lastName: 'last name',
              email: 'email'
            }
          }
        })
      })

      const expectedActions = [
        { type: 'USER_INFO_REQUEST' },
        {
          type: 'USER_INFO_SUCCESS',
          data: {
            userInfo: {
              accountID: 'account id',
              username: 'username',
              firstName: 'first name',
              lastName: 'last name',
              email: 'email'
            }
          }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getUserInfo()).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to fetch user info' }
        })
      })

      const expectedActions = [
        { type: 'USER_INFO_REQUEST' },
        {
          type: 'USER_INFO_FAILURE',
          error: { data: 'unable to fetch user info' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getUserInfo()).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  describe('logout', () => {
    it('dispatches logout', () => {
      const expectedActions = [{ type: 'LOGOUT' }]

      const store = mockStore({})

      store.dispatch<any>(logout())
      return expect(store.getActions()).toEqual(expectedActions)
    })
  })
})
