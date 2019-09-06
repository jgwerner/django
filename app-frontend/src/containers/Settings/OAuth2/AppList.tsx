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
  closeCreateAppSuccess,
  closeCreateAppError,
  closeDeleteAppSuccess,
  closeDeleteAppError
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
  createAppSuccess: boolean
  deleteAppSuccess: boolean
}

interface AppListMapDispatchToProps {
  deleteApp: (username: string, id: string) => void
  getApps: (username: string) => void
  closeCreateAppSuccess: () => void
  closeCreateAppError: () => void
  closeDeleteAppSuccess: () => void
  closeDeleteAppError: () => void
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
    const { username, getApps, createAppSuccess, deleteAppSuccess } = this.props
    if (
      createAppSuccess !== prev.createAppSuccess ||
      deleteAppSuccess !== prev.deleteAppSuccess
    ) {
      getApps(username)
    }
  }

  componentWillUnmount() {
    const {
      closeCreateAppSuccess,
      closeCreateAppError,
      closeDeleteAppSuccess,
      closeDeleteAppError
    } = this.props
    closeCreateAppSuccess()
    closeCreateAppError()
    closeDeleteAppSuccess()
    closeDeleteAppError()
  }

  render() {
    const { apps, appsFetched, deleteApp, username } = this.props
    return (
      <React.Fragment>
        {!appsFetched ? (
          <Container />
        ) : (
          <Container>
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
  username: state.home.user.username,
  createAppSuccess: state.settings.oauth2.createAppSuccess,
  deleteAppSuccess: state.settings.oauth2.deleteAppSuccess
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      deleteApp,
      getApps,
      closeCreateAppSuccess,
      closeCreateAppError,
      closeDeleteAppSuccess,
      closeDeleteAppError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AppList)
