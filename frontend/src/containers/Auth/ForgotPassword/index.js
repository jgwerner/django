import React from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { Switch, Route, Redirect, withRouter } from 'react-router-dom'
import { connect } from 'react-redux'
import { getFormValues } from 'redux-form'
import Loadable from 'react-loadable'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Link from 'components/atoms/Link'
import * as PasswordActions from './actions'

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

const ForgotPassword = props => {
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

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...PasswordActions
    },
    dispatch
  )

const mapStateToProps = state => ({
  requestValues: getFormValues('pwRequest')(state),
  confirmValues: getFormValues('pwConfirm')(state)
})

ForgotPassword.propTypes = {
  match: PropTypes.objectOf(PropTypes.array).isRequired,
  requestValues: PropTypes.objectOf(PropTypes.array).isRequired,
  confirmValues: PropTypes.objectOf(PropTypes.array).isRequired,
  resetPassword: PropTypes.func.isRequired,
  resetPasswordConfirm: PropTypes.func.isRequired
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ForgotPassword)
)
