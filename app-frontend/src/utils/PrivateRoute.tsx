import React from 'react'
import { Route, Redirect, RouteProps } from 'react-router-dom'
import { isLoggedIn } from './auth'

export interface PrivateRouteProps extends RouteProps {
  component: React.ComponentType<any>
}

const PrivateRoute = (props: PrivateRouteProps) => {
  const { component: Component, ...rest } = props
  return (
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
}

export default PrivateRoute
