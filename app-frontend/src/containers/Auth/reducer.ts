import { combineReducers } from 'redux'
import login, { LoginStoreState } from './Login/reducer'
import password, { PasswordStoreState } from './ForgotPassword/reducer'

export interface AuthStoreState {
  login: LoginStoreState
  password: PasswordStoreState
}

const auth = combineReducers({
  login,
  password
})

export default auth
