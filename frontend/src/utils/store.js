import { createStore, applyMiddleware, compose, combineReducers } from 'redux'
import { connectRouter, routerMiddleware } from 'connected-react-router'
import thunk from 'redux-thunk'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { reducer as reduxFormReducer } from 'redux-form'
import AuthReducer from 'containers/Auth/reducer'
import HomeReducer from 'containers/Home/reducer'
import ProjectReducer from 'containers/Project/reducer'
import { LOGOUT } from 'containers/Home/actions'
import SettingsReducer from 'containers/Settings/reducer'
import history from './history'

const initialState = {}
const enhancers = []
const middleware = [thunk, routerMiddleware(history)]

const persistConfig = {
  key: 'root',
  storage
}

const appReducer = combineReducers({
  router: connectRouter(history),
  form: reduxFormReducer,
  auth: AuthReducer,
  home: HomeReducer,
  project: ProjectReducer,
  settings: SettingsReducer
})

const rootReducer = (state, action) => {
  const newState = undefined
  if (action.type === LOGOUT) {
    return appReducer(newState, action)
  }
  return appReducer(state, action)
}

const composedEnhancers = compose(
  applyMiddleware(...middleware),
  ...enhancers
)

const persistedReducer = persistReducer(persistConfig, rootReducer)

export const store = createStore(
  persistedReducer,
  initialState,
  composedEnhancers
)

export const persistor = persistStore(store)
