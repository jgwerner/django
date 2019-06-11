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
} from 'components/AuthenticatedLayout/Header'
import Logo from 'components/Logo'
import { logout } from 'containers/Home/actions'
import history from 'utils/history'
import theme from 'utils/theme'
import Dropdown, { DropdownItem, DropdownSection } from 'components/Dropdown'
import Flex from 'components/atoms/Flex'
import Link from 'components/atoms/Link'
import { StoreState } from 'utils/store'
import Icon from 'components/Icon'
import { TextSpan } from 'components/atoms/Text'

interface DropdownToggleState {
  open: boolean
}

interface HeaderMapStateToProps {
  username: string
}

interface HeaderMapDispatchToProps {
  logout: () => void
}

type HeaderProps = HeaderMapStateToProps & HeaderMapDispatchToProps

const toggleOpen = (state: DropdownToggleState) => ({ open: !state.open })

class DropdownToggle extends React.PureComponent<
  HeaderProps,
  DropdownToggleState
> {
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
          <DropdownSection>
            <DropdownItem noHover>
              Signed in as <b>{username}</b>
            </DropdownItem>
          </DropdownSection>
          <DropdownSection>
            <DropdownItem onClick={() => history.push(`/settings`)}>
              <Icon type="settings" />{' '}
              <TextSpan p={1} verticalAlign="middle">
                Settings
              </TextSpan>
            </DropdownItem>
          </DropdownSection>
          <DropdownSection>
            <DropdownItem
              onClick={() =>
                window.open('https://docs.illumidesk.com', '_blank')
              }
            >
              Help Center
            </DropdownItem>
            <DropdownItem
              onClick={() =>
                window.open('https://status.illumidesk.com', '_blank')
              }
            >
              Status Page
            </DropdownItem>
            <DropdownItem
              onClick={() =>
                window.open('https://www.illumidesk.com/terms', '_blank')
              }
            >
              Terms
            </DropdownItem>
            <DropdownItem
              onClick={() =>
                window.open('https://www.illumidesk.com/privacy', '_blank')
              }
            >
              Privacy Policy
            </DropdownItem>
          </DropdownSection>
          <DropdownSection>
            <DropdownItem onClick={logout}>Logout</DropdownItem>
          </DropdownSection>
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
