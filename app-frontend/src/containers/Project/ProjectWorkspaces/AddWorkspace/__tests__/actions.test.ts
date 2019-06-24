import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { addWorkspace } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('add workspace actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('add workspace', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      const server = 'server object'
      const projectID = 'project id'
      const values = {
        name: 'server name'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { newWorkspaceData: ['new workspace data'] }
        })
      })

      const expectedActions = [
        { type: 'ADD_WORKSPACE_REQUEST' },
        {
          type: 'ADD_WORKSPACE_SUCCESS',
          data: { newWorkspaceData: ['new workspace data'] }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(addWorkspace(username, server, projectID, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      const username = 'username'
      const server = 'server object'
      const projectID = 'project id'
      const values = {
        name: 'server name'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to add new workspace' }
        })
      })

      const expectedActions = [
        { type: 'ADD_WORKSPACE_REQUEST' },
        {
          type: 'ADD_WORKSPACE_FAILURE',
          error: { data: 'unable to add new workspace' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(addWorkspace(username, server, projectID, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })
})
