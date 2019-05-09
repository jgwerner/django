import { combineReducers, AnyAction } from 'redux'
import {
  USER_INFO_FAILURE,
  USER_INFO_REQUEST,
  USER_INFO_SUCCESS,
  LOGOUT
} from './actions'
import projects, { ProjectListProps } from './ProjectList/reducer'
import addProject, { AddProjectProps } from './AddProject/reducer'

export interface UserStoreState {
  accountID: string
  username: string
  firstName: string
  lastName: string
  email: string
  profleInfo: any
  profileInfoFetched: boolean
}

const initialState = {
  accountID: '',
  username: '',
  firstName: '',
  lastName: '',
  email: '',
  profleInfo: {},
  profileInfoFetched: false
}

const user = (state = initialState, action: AnyAction) => {
  switch (action.type) {
    case USER_INFO_REQUEST:
      return {
        ...state
      }
    case USER_INFO_SUCCESS:
      return {
        ...state,
        accountID: action.data.id,
        username: action.data.username,
        firstName: action.data.first_name,
        lastName: action.data.last_name,
        email: action.data.email,
        profileInfo: action.data.profile,
        profileInfoFetched: true
      }
    case USER_INFO_FAILURE:
      return {
        ...state
      }
    case LOGOUT:
      return {
        ...state
      }
    default:
      return state
  }
}

export interface HomeStoreState {
  user: UserStoreState
  projects: ProjectListProps
  addProject: AddProjectProps
}

const homeReducer = combineReducers({
  user,
  projects,
  addProject
})

export default homeReducer
