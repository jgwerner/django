import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import {
  Switch,
  Route,
  Redirect,
  withRouter,
  RouteComponentProps
} from 'react-router-dom'
import { connect } from 'react-redux'
import { getFormValues } from 'redux-form'
import Loadable from 'react-loadable'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Link from 'components/atoms/Link'
import { resetPassword, resetPasswordConfirm } from './actions'
import { StoreState } from 'utils/store'

interface ForgotPasswordRouteProps {
  path: string
  url: string
}

interface ForgotPasswordMapStateToProps {
  requestValues: any
  confirmValues: any
}

interface ForgotPasswordMapDispatchToProps {
  resetPassword: (requestValues: any) => void
  resetPasswordConfirm: (confirmValues: any) => void
}

type ForgotPasswordProps = ForgotPasswordMapStateToProps &
  ForgotPasswordMapDispatchToProps &
  RouteComponentProps<ForgotPasswordRouteProps>

const AsyncRequest = Loadable({
  loader: () => import('./RequestForm'),
  loading: () => <div />
})
const AsyncSuccess = Loadable({
  loader: () => import('./RequestSuccess'),
  loading: () => <div />
})
const AsyncConfirm = Loadable({
  loader: () => import('./ConfirmForm'),
  loading: () => <div />
})

const ForgotPassword = (props: ForgotPasswordProps) => {
  const {
    match,
    requestValues,
    confirmValues,
    resetPassword,
    resetPasswordConfirm
  } = props
  return (
    <React.Fragment>
      <Heading my={4} textAlign="center">
        Reset your password
      </Heading>
      <Switch>
        <Route
          path={`${match.path}/request`}
          render={() => (
            <AsyncRequest onSubmit={() => resetPassword(requestValues)} />
          )}
        />
        <Route path={`${match.path}/next`} component={AsyncSuccess} />
        <Route
          path={`${match.path}/confirm`}
          render={() => (
            <AsyncConfirm
              onSubmit={() => resetPasswordConfirm(confirmValues)}
            />
          )}
        />
        <Redirect exact from={`${match.url}/`} to={`${match.path}/request`} />
      </Switch>
      <Container mx={4} mb={4} textAlign="center">
        <Link to="/auth">Return to login</Link>
      </Container>
    </React.Fragment>
  )
}

const mapDispatchToProps = (
  dispatch: Dispatch
): ForgotPasswordMapDispatchToProps =>
  bindActionCreators(
    {
      resetPassword,
      resetPasswordConfirm
    } as any,
    dispatch
  )

const mapStateToProps = (state: StoreState) => ({
  requestValues: getFormValues('pwRequest')(state),
  confirmValues: getFormValues('pwConfirm')(state)
})

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ForgotPassword)
)
