import React from 'react'
import { Switch, Route } from 'react-router-dom'
import Loadable from 'react-loadable'
import PrivateRoute from 'utils/PrivateRoute'
import AuthRoute from 'utils/AuthRoute'
import AuthenticatedLayout from 'components/AuthenticatedLayout'
import Content from 'components/AuthenticatedLayout/Content'
import Header from './Header'

const AsyncAuth = Loadable({
  loader: () => import('../Auth'),
  loading: () => <div />
})
const AsyncHome = Loadable({
  loader: () => import('../Home'),
  loading: () => <div />
})
const AsyncProject = Loadable({
  loader: () => import('../Project'),
  loading: () => <div />
})
const AsyncSettings = Loadable({
  loader: () => import('../Settings'),
  loading: () => <div />
})

const PrivateRoutes = () => (
  <AuthenticatedLayout>
    <Header />
    <Content>
      <Switch>
        <Route path="/projects/new" component={AsyncHome} />
        <Route path="/settings" component={AsyncSettings} />
        <Route path="/:userName/:projectName" component={AsyncProject} />
        <PrivateRoute path="/" component={AsyncHome} />
      </Switch>
    </Content>
  </AuthenticatedLayout>
)

const Main = () => (
  <React.Fragment>
    <Switch>
      <AuthRoute path="/auth" component={AsyncAuth} />
      <PrivateRoutes />
    </Switch>
  </React.Fragment>
)

export default Main
