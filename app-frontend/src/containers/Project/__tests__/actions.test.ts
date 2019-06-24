import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { getProject } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('project actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('get project', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      const projectName = 'project name'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: 'project details'
        })
      })

      const expectedActions = [
        { type: 'PROJECT_DETAILS_REQUEST' },
        {
          type: 'PROJECT_DETAILS_SUCCESS',
          data: 'project details'
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getProject(username, projectName)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      const projectName = 'project name'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to get project details' }
        })
      })

      const expectedActions = [
        { type: 'PROJECT_DETAILS_REQUEST' },
        {
          type: 'PROJECT_DETAILS_FAILURE',
          error: { data: 'unable to get project details' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getProject(username, projectName)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
