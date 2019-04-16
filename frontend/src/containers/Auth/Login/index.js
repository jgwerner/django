import React from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { getFormValues, propTypes } from 'redux-form'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Link from 'components/atoms/Link'
import Divider from 'components/atoms/Divider'
import Text from 'components/atoms/Text'
import theme from 'utils/theme'
import LoginForm from './Form'
import * as LoginActions from './actions'

const Login = props => {
  const { login, values, loggingIn } = props
  return (
    <React.Fragment>
      <Heading my={4} textAlign="center">
        Sign in
      </Heading>
      <LoginForm loggingIn={loggingIn} onSubmit={() => login(values)} />
      <Container mx={4} mb={4} textAlign="center">
        <Link to="/auth/password/">Forgot password?</Link>
      </Container>
      <Divider />
      <Text mx={4} textAlign="center" fontSize={1}>
        By using our platform, you agree to our {` `}
        <a
          style={{ textDecoration: 'none', color: theme.colors.link }}
          href="https://www.illumidesk.com/terms-and-conditions/"
        >
          Terms & Conditions
        </a>
        {` `} and {` `}
        <a
          style={{ textDecoration: 'none', color: theme.colors.link }}
          href="https://www.illumidesk.com/privacy-policy/"
        >
          {' '}
          Privacy Policy
        </a>
        .
      </Text>
    </React.Fragment>
  )
}

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...LoginActions
    },
    dispatch
  )

const mapStateToProps = state => ({
  values: getFormValues('login')(state),
  loggingIn: state.auth.login.loggingIn
})

Login.propTypes = {
  login: PropTypes.func.isRequired,
  loggingIn: PropTypes.bool.isRequired,
  ...propTypes
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Login)
