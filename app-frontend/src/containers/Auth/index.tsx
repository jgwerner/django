import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { Switch, Route, Redirect, RouteComponentProps } from 'react-router-dom'
import Loadable from 'react-loadable'
import Card from 'components/Card'
import Logo from 'components/Logo'
import Banner from 'components/Banner'
import Container from 'components/atoms/Container'
import { closeError, LoginActions } from './Login/actions'
import { StoreState } from 'utils/store'

interface AuthRouteProps {
  url: string
  path: string
}

interface AuthMapStateToProps {
  loginError: boolean
  errorMessage: string
}

interface AuthMapDispatchToProps {
  closeError: () => void
}

type AuthProps = AuthMapStateToProps &
  AuthMapDispatchToProps &
  RouteComponentProps<AuthRouteProps>

const AsyncLogin = Loadable({
  loader: () => import('./Login'),
  loading: () => <div />
})
const AsyncForgotPassword = Loadable({
  loader: () => import('./ForgotPassword'),
  loading: () => <div />
})

const AsyncTokenLogin = Loadable({
  loader: () => import('./Login/TokenLogin'),
  loading: () => <div />
})

const Auth = (props: AuthProps) => {
  // const handleBanner = () => {
  //   closeError()
  // }
  const displayError = () =>
    loginError ? (
      <Container>
        <Banner
          danger
          message={errorMessage}
          my={3}
          width={1 / 3}
          action={() => closeError()}
        />
      </Container>
    ) : (
      ''
    )
  // setTimeout(() => handleBanner(), 4000)

  const { match, loginError, errorMessage, closeError } = props
  return (
    <Container>
      {displayError()}
      <Card mx="auto" my={6} py={3} px={5} type="basic" width={1 / 3}>
        <Logo width="60px" mt={3} mb={4} />
        <Switch>
          <Redirect from={`${match.url}/`} to={`${match.url}/login`} exact />
          <Route path={`${match.path}/login`} component={AsyncLogin} />
          <Route
            path={`${match.path}/password/reset`}
            component={AsyncForgotPassword}
          />
          <Route
            path={`${match.path}/token-login`}
            component={AsyncTokenLogin}
          />
        </Switch>
      </Card>
    </Container>
  )
}

const mapStateToProps = (state: StoreState) => ({
  loginError: state.auth.login.loginError,
  errorMessage: state.auth.login.errorMessage
})

const mapDispatchToProps = (dispatch: Dispatch<LoginActions>) =>
  bindActionCreators(
    {
      closeError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Auth)
