import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import Heading from 'components/atoms/Heading'
import Text, { TextSpan } from 'components/atoms/Text'
import Container, { ContainerProps } from 'components/atoms/Container'
import Flex from 'components/atoms/Flex'
import Divider from 'components/atoms/Divider'
import Icon from 'components/Icon'
import {
  deleteApp,
  getApps,
  closeDeleteSuccess,
  closeCreateSuccess,
  closeCreateError
} from './actions'
import { StoreState } from 'utils/store'
import {
  Expand,
  Details,
  ToggleButton,
  DeleteButtonWrapper,
  DeleteButton,
  ToolTip
} from 'components/AppDetails'
import Banner from 'components/Banner'

interface AppState {
  open: boolean
}

interface AppProps {
  username: string
  name: string
  id: string
  clientID: string
  clientSecret: string
  deleteApp: (username: string, id: string) => void
}

interface AppListMapStateToProps {
  username: string
  apps: any
  appsFetched: boolean
  newApp: boolean
  appDeleted: boolean
  newAppError: boolean
}

interface AppListMapDispatchToProps {
  deleteApp: (username: string, id: string) => void
  getApps: (username: string) => void
  closeDeleteSuccess: () => void
  closeCreateSuccess: () => void
  closeCreateError: () => void
}

type AppListProps = AppListMapStateToProps & AppListMapDispatchToProps

interface ExpandProps extends ContainerProps {
  show?: boolean
}

const toggleDetails = (state: AppState) => ({ open: !state.open })

const App = class extends React.PureComponent<AppProps, AppState> {
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
          <TextSpan fontSize={5}>{name}</TextSpan>
          <ToggleButton mx={2} onClick={handleClick}>
            <Icon size="10" type={state.open ? 'arrowUp' : 'arrowDown'} />
          </ToggleButton>
        </Flex>
        <Expand show={state.open} p={2} mx={3} mt={-2}>
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
          <DeleteButtonWrapper mx={3} mb={3} color="danger" textAlign="end">
            <ToolTip>Delete App</ToolTip>
            <DeleteButton
              variation="icon"
              onClick={() => deleteApp(username, id)}
            >
              <Icon size="25" type="delete" />
            </DeleteButton>
          </DeleteButtonWrapper>
        </Expand>
      </Container>
    )
  }
}

const AppList = class extends React.PureComponent<AppListProps> {
  componentDidMount() {
    const { username, getApps } = this.props
    getApps(username)
  }

  componentDidUpdate(prev: any) {
    const { username, getApps, newApp, appDeleted } = this.props
    if (newApp !== prev.newApp || appDeleted !== prev.appDeleted) {
      getApps(username)
    }
  }

  componentWillUnmount() {
    const { closeDeleteSuccess, closeCreateSuccess } = this.props
    closeCreateSuccess()
    closeDeleteSuccess()
  }

  render() {
    const {
      apps,
      appsFetched,
      deleteApp,
      username,
      appDeleted,
      closeDeleteSuccess,
      closeCreateSuccess,
      newApp,
      newAppError,
      closeCreateError
    } = this.props
    return (
      <React.Fragment>
        {!appsFetched ? (
          <Container />
        ) : (
          <Container>
            {newApp ? (
              <Banner
                success
                width={1}
                message="New application created"
                action={() => closeCreateSuccess()}
              />
            ) : (
              ''
            )}
            {newAppError ? (
              <Banner
                danger
                width={1}
                message="Error creating new app"
                action={() => closeCreateError()}
              />
            ) : (
              ''
            )}
            {appDeleted ? (
              <Banner
                success
                width={1}
                message="Delete Application Request Succeeded"
                action={() => closeDeleteSuccess()}
              />
            ) : (
              ''
            )}
            {apps.map((i: any) => (
              <Container key={i.id}>
                <App
                  username={username}
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

const mapStateToProps = (state: StoreState) => ({
  apps: state.settings.oauth2.apps,
  appsFetched: state.settings.oauth2.appsFetched,
  newApp: state.settings.oauth2.newApp,
  appDeleted: state.settings.oauth2.appDeleted,
  username: state.home.user.username,
  newAppError: state.settings.oauth2.newAppError
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      deleteApp,
      getApps,
      closeDeleteSuccess,
      closeCreateSuccess,
      closeCreateError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AppList)
