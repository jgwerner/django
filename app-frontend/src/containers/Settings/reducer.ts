import { combineReducers } from 'redux'
import account from './Account/reducer'
import oauth2, { OAuth2StoreState } from './OAuth2/reducer'

const settingsReducer = combineReducers({
  account,
  oauth2
})

export interface SettingsStoreState {
  oauth2: OAuth2StoreState
}

export default settingsReducer
