import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { RouteComponentProps, withRouter } from 'react-router'
import qs from 'qs'
import { tokenLogin, TokenLoginActions } from './actions'
import Text from 'components/atoms/Text'

interface TokenLoginRouteProps {
  params: string
}

interface TokenLoginMapDispatchToProps {
  tokenLogin: (tempToken: string) => void
}

type TokenLoginProps = TokenLoginMapDispatchToProps &
  RouteComponentProps<TokenLoginRouteProps>

const TokenLogin = class extends React.PureComponent<TokenLoginProps> {
  componentDidMount() {
    const { location, tokenLogin } = this.props
    const params = qs.parse(location.search.slice(1))
    tokenLogin(params.token)
  }

  render() {
    return (
      <React.Fragment>
        <Text textAlign="center" mt="20%" fontSize={5}>
          Logging in...
        </Text>
      </React.Fragment>
    )
  }
}

const mapDispatchToProps = (dispatch: Dispatch<TokenLoginActions>) =>
  bindActionCreators(
    {
      tokenLogin
    },
    dispatch
  )

export default withRouter(
  connect(
    null,
    mapDispatchToProps
  )(TokenLogin)
)
