import React from 'react'
import { Switch, Route, Redirect } from 'react-router-dom'
import Loadable from 'react-loadable'
import Card from 'components/Card'
import Logo from 'components/Logo'

const AsyncLogin = Loadable({
  loader: () => import('./Login'),
  loading: () => <div />
})
const AsyncForgotPassword = Loadable({
  loader: () => import('./ForgotPassword'),
  loading: () => <div />
})

const Auth = props => {
  const { match } = props
  return (
    <Card mx="auto" my={6} py={3} px={5} type="basic" width={1 / 3}>
      <Logo width="60px" mt={3} mb={4} />
      <Switch>
        <Redirect from={`${match.url}/`} to={`${match.url}/login`} exact />
        <Route path={`${match.path}/login`} component={AsyncLogin} />
        <Route
          path={`${match.path}/password`}
          component={AsyncForgotPassword}
        />
      </Switch>
    </Card>
  )
}

export default Auth
