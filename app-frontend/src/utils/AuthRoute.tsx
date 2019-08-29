import React from 'react'
import { Route, Redirect, RouteProps } from 'react-router-dom'
import { isLoggedIn } from './auth'

export interface AuthRouteProps extends RouteProps {
  component: React.ComponentType<any>
}

const AuthRoute = (props: AuthRouteProps) => {
  const { component: Component, ...rest } = props
  return (
    <Route
      {...rest}
      render={props =>
        !isLoggedIn() || props.location.pathname.includes('token-login') ? (
          <Component {...props} />
        ) : (
          <Redirect
            to={{
              pathname: '/',
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

export default AuthRoute
