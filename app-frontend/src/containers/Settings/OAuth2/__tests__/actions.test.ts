import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { getApps, createApp, deleteApp } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('ouath2 settings actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('get apps', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { apps: 'list of apps' }
        })
      })

      const expectedActions = [
        { type: 'GET_APPS_REQUEST' },
        {
          type: 'GET_APPS_SUCCESS',
          data: { apps: 'list of apps' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getApps(username)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to retrieve apps' }
        })
      })

      const expectedActions = [
        { type: 'GET_APPS_REQUEST' },
        {
          type: 'GET_APPS_FAILURE',
          error: { data: 'unable to retrieve apps' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getApps(username)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  describe('create app', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      const appName = 'new app'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { newApp: 'new app object' }
        })
      })

      const expectedActions = [
        { type: 'NEW_APP_REQUEST' },
        { type: '@@redux-form/RESET', meta: { form: 'newApp' } },
        {
          type: 'NEW_APP_SUCCESS',
          data: { newApp: 'new app object' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(createApp(username, appName)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      const appName = 'new app'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to create new app' }
        })
      })

      const expectedActions = [
        { type: 'NEW_APP_REQUEST' },
        {
          type: 'NEW_APP_FAILURE',
          error: { data: 'unable to create new app' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(createApp(username, appName)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  describe('delete account', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      const appID = 'appID'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'app deleted'
        })
      })

      const expectedActions = [
        { type: 'DELETE_APP_REQUEST' },
        {
          type: 'DELETE_APP_SUCCESS',
          data: 'app deleted'
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(deleteApp(username, appID)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      const appID = 'appID'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to delete app' }
        })
      })

      const expectedActions = [
        { type: 'DELETE_APP_REQUEST' },
        {
          type: 'DELETE_APP_FAILURE',
          error: { data: 'unable to delete app' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(deleteApp(username, appID)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
