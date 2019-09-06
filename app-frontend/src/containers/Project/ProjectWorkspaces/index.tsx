import React, { Fragment } from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Loadable from 'react-loadable'
import {
  getWorkspaces,
  GetWorkspacesActions,
  closeServerError
} from './actions'
import { getProject, ProjectDetailsActions } from '../actions'
import { StoreState } from 'utils/store'
import {
  closeUpdateProjectError,
  closeUpdateProjectSuccess
} from '../Settings/actions'

interface WorkspacesRouteProps {
  userName: string
  projectName: string
  url: string
}

interface WorkspacesMapStateToProps {
  projectDetails: any
  newWorkspace: boolean
  workspaces: any
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
  closeServerError: () => void
  closeUpdateProjectError: () => void
  closeUpdateProjectSuccess: () => void
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
    const {
      match,
      getWorkspaces,
      projectDetails,
      closeUpdateProjectError,
      closeUpdateProjectSuccess
    } = this.props
    getWorkspaces(match.params.userName, projectDetails.id)
    closeUpdateProjectError()
    closeUpdateProjectSuccess()
  }

  componentDidUpdate(prev: any) {
    const { match, projectDetails, getWorkspaces, newWorkspace } = this.props
    if (prev.projectDetails.id !== projectDetails.id) {
      getWorkspaces(match.params.userName, projectDetails.id)
    } else if (prev.newWorkspace !== newWorkspace) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
  }

  componentWillUnmount() {
    const { closeServerError } = this.props
    closeServerError()
  }

  render() {
    const { projectDetails, workspaces, match } = this.props
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
  projectDetails: project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch): WorkspacesMapDispatchToProps =>
  bindActionCreators(
    {
      getProject,
      getWorkspaces,
      closeServerError,
      closeUpdateProjectError,
      closeUpdateProjectSuccess
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(withRouter(Workspaces))
