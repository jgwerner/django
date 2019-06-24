import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import {
  getServerSizes,
  getWorkspaces,
  startServer,
  stopServer,
  deleteServer,
  updateStatus
} from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('project workspace actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('get server size options', () => {
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'server size options'
        })
      })

      const expectedActions = [
        { type: 'GET_SIZES_REQUEST' },
        {
          type: 'GET_SIZES_SUCCESS',
          data: 'server size options'
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getServerSizes()).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to get server size options' }
        })
      })

      const expectedActions = [
        { type: 'GET_SIZES_REQUEST' },
        {
          type: 'GET_SIZES_FAILURE',
          error: { data: 'unable to get server size options' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getServerSizes()).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })

  describe('get workspace', () => {
    const username = 'username'
    const projectID = 'project id'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'workspace details'
        })
      })

      const expectedActions = [
        { type: 'GET_WORKSPACES_REQUEST' },
        {
          type: 'GET_WORKSPACES_SUCCESS',
          data: 'workspace details'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(getWorkspaces(username, projectID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to get workspace details' }
        })
      })

      const expectedActions = [
        { type: 'GET_WORKSPACES_REQUEST' },
        {
          type: 'GET_WORKSPACES_FAILURE',
          error: { data: 'unable to get workspace details' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(getWorkspaces(username, projectID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('start server', () => {
    const username = 'username'
    const projectID = 'project id'
    const workspaceID = 'workspace id'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'server started'
        })
      })

      const expectedActions = [
        { type: 'START_SERVER_REQUEST' },
        {
          type: 'START_SERVER_SUCCESS',
          data: 'server started'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(startServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to start server' }
        })
      })

      const expectedActions = [
        { type: 'START_SERVER_REQUEST' },
        {
          type: 'START_SERVER_FAILURE',
          error: { data: 'unable to start server' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(startServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('stop server', () => {
    const username = 'username'
    const projectID = 'project id'
    const workspaceID = 'workspace id'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'server stopped'
        })
      })

      const expectedActions = [
        { type: 'STOP_SERVER_REQUEST' },
        {
          type: 'STOP_SERVER_SUCCESS',
          data: 'server stopped'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(stopServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to stop server' }
        })
      })

      const expectedActions = [
        { type: 'STOP_SERVER_REQUEST' },
        {
          type: 'STOP_SERVER_FAILURE',
          error: { data: 'unable to stop server' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(stopServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('delete server', () => {
    const username = 'username'
    const projectID = 'project id'
    const workspaceID = 'workspace id'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'server deleted'
        })
      })

      const expectedActions = [
        { type: 'DELETE_SERVER_REQUEST' },
        {
          type: 'DELETE_SERVER_SUCCESS',
          data: 'server deleted'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(deleteServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to delete server' }
        })
      })

      const expectedActions = [
        { type: 'DELETE_SERVER_REQUEST' },
        {
          type: 'DELETE_SERVER_FAILURE',
          error: { data: 'unable to delete server' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(deleteServer(username, projectID, workspaceID))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('update status', () => {
    const status = 'updated status'
    it('dispatches correct action and payload', () => {
      const expectedActions = {
        type: 'UPDATE_STATUS',
        data: 'updated status'
      }

      expect(updateStatus(status)).toEqual(expectedActions)
    })
  })
})
