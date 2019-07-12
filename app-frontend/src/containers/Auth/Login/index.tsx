import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { getFormValues } from 'redux-form'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Link from 'components/atoms/Link'
import Divider from 'components/atoms/Divider'
import Text from 'components/atoms/Text'
import theme from 'utils/theme'
import LoginForm from './Form'
import { login, LoginActions, closeError } from './actions'
import { StoreState } from 'utils/store'

interface LoginMapStateToProps {
  values: any
}

interface LoginMapDispatchToProps {
  login: (values: any) => void
  closeError: () => void
}

type LoginProps = LoginMapStateToProps & LoginMapDispatchToProps

const Login = class extends React.PureComponent<LoginProps> {
  componentWillUnmount() {
    const { closeError } = this.props
    closeError()
  }
  render() {
    const { login, values } = this.props
    return (
      <React.Fragment>
        <Heading my={4} textAlign="center">
          Sign in
        </Heading>
        <LoginForm onSubmit={() => login(values)} />
        <Container mx={4} mb={4} textAlign="center">
          <Link to="/auth/password/reset">Forgot password?</Link>
        </Container>
        <Divider />
        <Text mx={4} textAlign="center" fontSize={1}>
          By using our platform, you agree to our {` `}
          <a
            style={{ textDecoration: 'none', color: theme.colors.link }}
            href="https://www.illumidesk.com/terms"
          >
            Terms & Conditions
          </a>
          {` `} and {` `}
          <a
            style={{ textDecoration: 'none', color: theme.colors.link }}
            href="https://www.illumidesk.com/privacy"
          >
            {' '}
            Privacy Policy
          </a>
          .
        </Text>
      </React.Fragment>
    )
  }
}

const mapDispatchToProps = (dispatch: Dispatch<LoginActions>) =>
  bindActionCreators(
    {
      login,
      closeError
    },
    dispatch
  )

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('login')(state)
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Login)
