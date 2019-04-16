import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import Avatar from 'react-avatar'
import {
  Header as HeaderWrapper,
  HeaderItemsLeft,
  HeaderItemsRight,
  Item,
  DownArrow,
  DropdownWrapper
} from 'components/AuthenticatedLayout/Header'
import Logo from 'components/Logo'
import * as HomeActions from 'containers/Home/actions'
import history from 'utils/history'
import theme from 'utils/theme'
import Dropdown from 'components/Dropdown'
import Flex from 'components/atoms/Flex'
import Link from 'components/atoms/Link'

const toggleOpen = state => ({ open: !state.open })

class DropdownToggle extends React.PureComponent {
  state = {
    open: false
  }

  handleClick = () => this.setState(toggleOpen)

  render() {
    const { handleClick, state } = this
    const { username, logout } = this.props
    return (
      <DropdownWrapper onClick={handleClick}>
        <Flex alignItems="center">
          <Item>
            <Avatar
              name={username}
              size="35px"
              textSizeRatio={2}
              round
              color={theme.colors.gray7}
            />
          </Item>
          <Item>
            <DownArrow />
          </Item>
        </Flex>
        <Dropdown show={state.open}>
          <Dropdown.Item onClick={() => history.push(`/${username}`)}>
            Profile
          </Dropdown.Item>
          <Dropdown.Item onClick={() => history.push(`/settings`)}>
            Settings
          </Dropdown.Item>
          <Dropdown.Item onClick={logout}>Logout</Dropdown.Item>
        </Dropdown>
      </DropdownWrapper>
    )
  }
}

const Header = props => {
  const { username, logout } = props
  return (
    <HeaderWrapper>
      <HeaderItemsLeft width={1 / 2}>
        <Item>
          <Link to="/">
            <Logo />
          </Link>
        </Item>
      </HeaderItemsLeft>
      <HeaderItemsRight>
        <DropdownToggle username={username} logout={logout} />
      </HeaderItemsRight>
    </HeaderWrapper>
  )
}

const mapStateToProps = state => ({
  username: state.home.user.username
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...HomeActions
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Header)
