import moxios from 'moxios'
import thunk from 'redux-thunk'
import configureMockStore from 'redux-mock-store'
import { getProjectList } from '../actions'

const middlewares = [thunk]
const mockStore = configureMockStore(middlewares)

describe('project list actions', () => {
  beforeEach(() => {
    moxios.install()
  })

  afterEach(() => {
    moxios.uninstall()
  })

  describe('project list', () => {
    it('dispatches correct action and payload', () => {
      const username = 'username'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.respondWith({
          status: 200,
          response: { projectList: ['project list'] }
        })
      })

      const expectedActions = [
        { type: 'PROJECT_LIST_REQUEST' },
        {
          type: 'PROJECT_LIST_SUCCESS',
          data: { projectList: ['project list'] }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getProjectList(username)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })

    it('dispatches failure', () => {
      const username = 'username'
      moxios.wait(() => {
        const request = moxios.requests.mostRecent()
        request.reject({
          status: 400,
          response: { data: 'unable to load projects' }
        })
      })

      const expectedActions = [
        { type: 'PROJECT_LIST_REQUEST' },
        {
          type: 'PROJECT_LIST_FAILURE',
          error: { data: 'unable to load projects' }
        }
      ]

      const store = mockStore({})

      return store.dispatch<any>(getProjectList(username)).then(() => {
        expect(store.getActions()).toEqual(expectedActions)
      })
    })
  })
})
