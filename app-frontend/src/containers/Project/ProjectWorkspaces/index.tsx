import React, { Fragment } from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Loadable from 'react-loadable'
import { getWorkspaces, GetWorkspacesActions, closeError } from './actions'
import { getProject, ProjectDetailsActions } from '../actions'
import { StoreState } from 'utils/store'
import Container from 'components/atoms/Container'
import Banner from 'components/Banner'

interface WorkspacesRouteProps {
  userName: string
  projectName: string
  url: string
}

interface WorkspacesMapStateToProps {
  projectDetails: any
  newWorkspace: boolean
  workspaces: any
  startServerError: boolean
}

interface WorkspacesMapDispatchToProps {
  getProject: (
    userName: string,
    projectName: string
  ) => (dispatch: Dispatch<ProjectDetailsActions>) => void
  getWorkspaces: (
    userName: string,
    id: string
  ) => (dispatch: Dispatch<GetWorkspacesActions>) => void
  closeError: () => void
}

type WorkspacesProps = WorkspacesMapDispatchToProps &
  WorkspacesMapStateToProps &
  RouteComponentProps<WorkspacesRouteProps>

const AsyncNoWorkspaces = Loadable({
  loader: () => import('./NoWorkspaces'),
  loading: () => <div />
})

const AsyncWorkspaceTable = Loadable({
  loader: () => import('./WorkspaceTable'),
  loading: () => <div />
})

class Workspaces extends React.Component<WorkspacesProps> {
  componentDidMount() {
    const { match, getWorkspaces, projectDetails } = this.props
    getWorkspaces(match.params.userName, projectDetails.id)
  }

  componentDidUpdate(prev: any) {
    const { match, projectDetails, getWorkspaces, newWorkspace } = this.props
    if (prev.projectDetails.id !== projectDetails.id) {
      getWorkspaces(match.params.userName, projectDetails.id)
    } else if (prev.newWorkspace !== newWorkspace) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
  }

  render() {
    const {
      projectDetails,
      workspaces,
      match,
      startServerError,
      closeError
    } = this.props
    return (
      <Fragment>
        {projectDetails.name === match.params.projectName ? (
          <Fragment>
            {workspaces.length === 0 ? (
              <Fragment>
                <AsyncNoWorkspaces />
              </Fragment>
            ) : (
              <Fragment>
                {startServerError ? (
                  <Container>
                    <Banner
                      danger
                      message="The server could not be found. Please delete the server and create a new one."
                      my={3}
                      width={1}
                      action={() => closeError()}
                    />
                  </Container>
                ) : (
                  ''
                )}
                {workspaces[0].project === projectDetails.id ? (
                  <AsyncWorkspaceTable statusURL={workspaces[0].status_url} />
                ) : (
                  <Fragment />
                )}
              </Fragment>
            )}
          </Fragment>
        ) : (
          <Fragment />
        )}
      </Fragment>
    )
  }
}

const mapStateToProps = ({
  project
}: StoreState): WorkspacesMapStateToProps => ({
  workspaces: project.workspaces.servers.workspaces,
  newWorkspace: project.workspaces.add.newWorkspace,
  projectDetails: project.details.projectDetails,
  startServerError: project.workspaces.servers.startServerError
})

const mapDispatchToProps = (dispatch: Dispatch): WorkspacesMapDispatchToProps =>
  bindActionCreators(
    {
      getProject,
      getWorkspaces,
      closeError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(withRouter(Workspaces))
