import React from 'react'
import { Route, Redirect } from 'react-router-dom'
import { isLoggedIn } from './auth'

const PrivateRoute = ({ component: Component, ...rest }) => (
  <Route
    {...rest}
    render={props =>
      isLoggedIn() ? (
        <Component {...props} />
      ) : (
        <Redirect
          to={{
            pathname: '/auth/login',
            state: {
              /* eslint-disable */
                ...props.location.state,
                next: props.location.pathname,
                /* eslint-enable */
            }
          }}
        />
      )
    }
  />
)

export default PrivateRoute
