import { combineReducers } from 'redux'
import account from './Account/reducer'
import oauth2 from './OAuth2/reducer'

const settingsReducer = combineReducers({
  account,
  oauth2
})

export default settingsReducer
