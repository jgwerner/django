import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { addProject } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('add project actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('add project', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      const values = {
        name: 'project name',
        description: 'project description',
        private: 'true'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { addProjectData: ['new project data'] }
        })
      })

      const expectedActions = [
        { type: 'ADD_PROJECT_REQUEST' },
        {
          type: 'ADD_PROJECT_SUCCESS',
          data: { addProjectData: ['new project data'] }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(addProject(username, values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      const values = {
        name: 'project name',
        description: 'project description',
        private: 'true'
      }
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to add new project' }
        })
      })

      const expectedActions = [
        { type: 'ADD_PROJECT_REQUEST' },
        {
          type: 'ADD_PROJECT_FAILURE',
          error: { data: 'unable to add new project' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(addProject(username, values)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
