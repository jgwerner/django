import { createStore, applyMiddleware, compose, combineReducers, AnyAction } from 'redux'
import { connectRouter, routerMiddleware } from 'connected-react-router'
import thunk from 'redux-thunk'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { reducer as reduxFormReducer } from 'redux-form'
import AuthReducer, { AuthStoreState } from '../containers/Auth/reducer'
import HomeReducer, { HomeStoreState } from '../containers/Home/reducer'
import ProjectReducer, { ProjectStoreState } from '../containers/Project/reducer'
import { LOGOUT } from '../containers/Home/actions'
import SettingsReducer, {SettingsStoreState} from '../containers/Settings/reducer'
import history from './history'

const initialState = {}
const middleware = [thunk, routerMiddleware(history)]

const persistConfig = {
  key: 'root',
  storage
}

export interface StoreState {
  home: HomeStoreState,
  project: ProjectStoreState,
  auth: AuthStoreState,
  settings: SettingsStoreState
}

const appReducer = combineReducers({
  router: connectRouter(history),
  form: reduxFormReducer,
  auth: AuthReducer,
  home: HomeReducer,
  project: ProjectReducer,
  settings: SettingsReducer
})

const rootReducer = (state: any, action: AnyAction) => {
  const newState = undefined
  if (action.type === LOGOUT) {
    return appReducer(newState, action)
  }
  return appReducer(state, action)
}

const composedEnhancers = compose(
  applyMiddleware(...middleware),
)

const persistedReducer = persistReducer(persistConfig, rootReducer)

export const store = createStore(
  persistedReducer,
  initialState,
  composedEnhancers
)

export const persistor = persistStore(store)
