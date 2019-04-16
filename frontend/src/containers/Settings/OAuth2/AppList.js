import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import Heading from 'components/atoms/Heading'
import Text from 'components/atoms/Text'
import Container from 'components/atoms/Container'
import Flex from 'components/atoms/Flex'
import Divider from 'components/atoms/Divider'
import styled from 'styled-components'
import Icon from 'components/Icon'
import * as OAuth2Actions from './actions'

const Expand = styled(Container)`
  display: ${props => (props.show ? 'block' : 'none')};
`
const Details = styled(Container)`
  word-break: break-word;
`
const ToggleButton = styled(Container)`
  &:hover {
    cursor: pointer;
  }
`

const DeleteButton = styled(Container)`
  &:hover {
    cursor: pointer;
  }
`

const toggleDetails = state => ({ open: !state.open })

const App = class extends React.PureComponent {
  state = {
    open: false
  }

  handleClick = () => this.setState(toggleDetails)

  render() {
    const { handleClick, state } = this
    const { name, id, clientID, clientSecret, deleteApp, username } = this.props
    return (
      <Container>
        <Flex m={3}>
          <Text.Span fontSize={5}>{name}</Text.Span>
          <ToggleButton mx={2} onClick={handleClick}>
            <Icon size="10" type={state.open ? 'arrowUp' : 'arrowDown'} />
          </ToggleButton>
        </Flex>
        <Expand show={state.open} type="contentPartial" p={2} mx={3} mt={-2}>
          <Heading bold size="h4">
            Details
          </Heading>
          <Divider />
          <Container m={3}>
            <Heading bold sub color="gray7">
              Client ID
            </Heading>
            <Details m={1} p={2} bg="gray1">
              <Text fontSize={2} color="textLight">
                {clientID}
              </Text>
            </Details>
          </Container>
          <Container m={3}>
            <Heading bold sub color="gray7">
              Client Secret
            </Heading>
            <Details m={1} p={2} bg="gray1">
              <Text fontSize={2} color="textLight">
                {clientSecret}
              </Text>
            </Details>
          </Container>
          <Divider />
          <DeleteButton
            mx={3}
            mb={3}
            color="danger"
            textAlign="end"
            onClick={() => deleteApp(username, id)}
          >
            <Icon size="25" type="delete" />
          </DeleteButton>
        </Expand>
      </Container>
    )
  }
}

const AppList = class extends React.PureComponent {
  componentDidMount() {
    const { username, getApps } = this.props
    getApps(username)
  }

  componentDidUpdate(prev) {
    const { username, getApps, newApp, appDeleted } = this.props
    if (newApp !== prev.newApp || appDeleted !== prev.appDeleted) {
      getApps(username)
    }
  }

  render() {
    const { apps, appsFetched, deleteApp } = this.props
    return (
      <React.Fragment>
        {!appsFetched ? (
          <Container />
        ) : (
          <Container>
            {apps.map(i => (
              <Container key={i.id}>
                <App
                  name={i.name}
                  clientID={i.client_id}
                  clientSecret={i.client_secret}
                  id={i.id}
                  deleteApp={deleteApp}
                />
              </Container>
            ))}
          </Container>
        )}
      </React.Fragment>
    )
  }
}

const mapStateToProps = state => ({
  apps: state.settings.oauth2.apps,
  appsFetched: state.settings.oauth2.appsFetched,
  newApp: state.settings.oauth2.newApp,
  appDeleted: state.settings.oauth2.appDeleted,
  username: state.home.user.username
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...OAuth2Actions
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(AppList)
)
