import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { updateProject, changeVisibility, deleteProject } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('project settings actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('get server size options', () => {
    const username = 'username'
    const projectID = 'project id'
    const values = {
      name: 'project name',
      description: 'project description'
    }
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'project updated'
        })
      })

      const expectedActions = [
        { type: 'UPDATE_PROJECT_REQUEST' },
        {
          type: 'UPDATE_PROJECT_SUCCESS',
          data: 'project updated'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(updateProject(username, projectID, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to update project' }
        })
      })

      const expectedActions = [
        { type: 'UPDATE_PROJECT_REQUEST' },
        {
          type: 'UPDATE_PROJECT_FAILURE',
          error: { data: 'unable to update project' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(updateProject(username, projectID, values))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('change project visibility', () => {
    const username = 'username'
    const projectName = 'project name'
    const visibility = 'project visibility'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'visibility updated'
        })
      })

      const expectedActions = [
        { type: 'CHANGE_VISIBILITY_REQUEST' },
        {
          type: 'CHANGE_VISIBILITY_SUCCESS',
          data: 'visibility updated'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(changeVisibility(username, projectName, visibility))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to change visibility' }
        })
      })

      const expectedActions = [
        { type: 'CHANGE_VISIBILITY_REQUEST' },
        {
          type: 'CHANGE_VISIBILITY_FAILURE',
          error: { data: 'unable to change visibility' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(changeVisibility(username, projectName, visibility))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })

  describe('delete project', () => {
    const username = 'username'
    const projectName = 'project name'
    it('dispatches correct action and payload', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'project deleted'
        })
      })

      const expectedActions = [
        { type: 'DELETE_PROJECT_REQUEST' },
        {
          type: 'DELETE_PROJECT_SUCCESS',
          data: 'project deleted'
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(deleteProject(username, projectName))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })

    it('dispatches failure', () => {
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to delete project' }
        })
      })

      const expectedActions = [
        { type: 'DELETE_PROJECT_REQUEST' },
        {
          type: 'DELETE_PROJECT_FAILURE',
          error: { data: 'unable to delete project' }
        }
      ]

      const store = mockStore({})

      return store
        .dispatch<any>(deleteProject(username, projectName))
        .then(() => {
          expect(store.getActions()).toEqual(expectedActions)
        })
    })
  })
})
