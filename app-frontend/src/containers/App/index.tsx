import React from 'react'
import { Provider } from 'react-redux'
import { ConnectedRouter } from 'connected-react-router'
import { PersistGate } from 'redux-persist/integration/react'
import { ThemeProvider } from 'styled-components'
import { store, persistor } from '../../utils/store'
import history from '../../utils/history'
import theme from '../../utils/theme'
import Global from '../../utils/theme/global'
import Main from '../Main'

const App = () => (
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <ConnectedRouter history={history}>
        <ThemeProvider theme={theme}>
          <React.Fragment>
            <Global />
            <Main />
          </React.Fragment>
        </ThemeProvider>
      </ConnectedRouter>
    </PersistGate>
  </Provider>
)

export default App
