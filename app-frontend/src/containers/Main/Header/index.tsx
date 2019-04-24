import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import Avatar from 'react-avatar'
import {
  Header as HeaderWrapper,
  HeaderItemsLeft,
  HeaderItemsRight,
  Item,
  DownArrow,
  DropdownWrapper
} from '../../../components/AuthenticatedLayout/Header'
import Logo from '../../../components/Logo'
import {logout} from '../../../containers/Home/actions'
import history from '../../../utils/history'
import theme from '../../../utils/theme'
import Dropdown, {DropdownItem} from '../../../components/Dropdown'
import Flex from '../../../components/atoms/Flex'
import Link from '../../../components/atoms/Link'
import { StoreState } from '../../../utils/store';

interface DropdownToggleState {
  open: boolean
}

interface HeaderMapStateToProps {
  username: string,
}

interface HeaderMapDispatchToProps {
  logout: () => void
}

type HeaderProps = HeaderMapStateToProps & HeaderMapDispatchToProps


const toggleOpen = (state: DropdownToggleState) => ({ open: !state.open })

class DropdownToggle extends React.PureComponent<HeaderProps, DropdownToggleState> {
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
          <DropdownItem onClick={() => history.push(`/${username}`)}>
            Profile
          </DropdownItem>
          <DropdownItem onClick={() => history.push(`/settings`)}>
            Settings
          </DropdownItem>
          <DropdownItem onClick={logout}>Logout</DropdownItem>
        </Dropdown>
      </DropdownWrapper>
    )
  }
}

const Header = (props: HeaderProps) => {
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

const mapStateToProps = (state: StoreState) => ({
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
bindActionCreators(
{
  logout
},
dispatch
)

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Header)
