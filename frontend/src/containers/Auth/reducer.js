import { combineReducers } from 'redux'
import login from './Login/reducer'
import password from './ForgotPassword/reducer'

const auth = combineReducers({
  login,
  password
})

export default auth
