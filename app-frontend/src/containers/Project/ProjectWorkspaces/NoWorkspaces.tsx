import React from 'react'
import { withRouter, Route, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Link from '../../../components/atoms/Link'
import Button from '../../../components/atoms/Button'
import Loadable from 'react-loadable'
import Container from '../../../components/atoms/Container'
import Text from '../../../components/atoms/Text'
import Heading from '../../../components/atoms/Heading'
import { getServerSizes } from './actions'
import { StoreState } from '../../../utils/store'

interface NoWorkspacesRouteProps {
  url: string
  userName: string
  projectName: string
}

interface NoWorkspacesMapStateToProps {
  projectDetails: any
  serverSizes: any
}

interface NoWorkspacesMapDispatchToProps {
  getServerSizes: () => void
}

type NoWorkspacesProps = NoWorkspacesMapStateToProps &
  NoWorkspacesMapDispatchToProps &
  RouteComponentProps<NoWorkspacesRouteProps>

const AsyncAddWorkspace = Loadable({
  loader: () => import('./AddWorkspace'),
  loading: () => <div />
})

const NoWorkspaces = class extends React.PureComponent<NoWorkspacesProps> {
  componentDidMount() {
    const { getServerSizes } = this.props
    getServerSizes()
  }

  render() {
    const { match, projectDetails, serverSizes } = this.props
    return (
      <Container>
        {serverSizes.length ? (
          <Container width="fit-content" m="auto" textAlign="center" pt={4}>
            <Container m={4}>
              <Heading size="h4" color="textLight">
                No workspaces
              </Heading>
              <Text color="textLight">
                Add a workspace to begin working in a data science environment
              </Text>
            </Container>
            <Link to={`${match.url}/new`}>
              <Button m="auto">Add workspace</Button>
            </Link>
            <Route
              path={`${match.url}/new`}
              render={(props: any) => (
                <AsyncAddWorkspace
                  {...props}
                  server={serverSizes}
                  projectDetails={projectDetails}
                />
              )}
            />
          </Container>
        ) : (
          <Container />
        )}
      </Container>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  serverSizes: state.project.workspaces.servers.serverSizes,
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getServerSizes
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(NoWorkspaces)
)
