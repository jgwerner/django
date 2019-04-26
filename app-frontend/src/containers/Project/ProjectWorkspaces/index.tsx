import React, { Fragment } from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Loadable from 'react-loadable'
import {getWorkspaces, GetWorkspacesActions} from './actions'
import {getProject, ProjectDetailsActions} from '../actions'
import { StoreState } from 'utils/store'

interface WorkspacesRouteProps {
  userName: string,
  projectName: string
  url: string
}

interface WorkspacesMapStateToProps {
  projectDetails:any,
  newWorkspace: boolean,
  workspaces: any
}

interface WorkspacesMapDispatchToProps {
  getProject: (userName: string, projectName: string) => (dispatch: Dispatch<ProjectDetailsActions>) => void,
  getWorkspaces: (userName: string, id: string) => (dispatch: Dispatch<GetWorkspacesActions>) => void,
}

type WorkspacesProps = WorkspacesMapDispatchToProps & WorkspacesMapStateToProps & RouteComponentProps<WorkspacesRouteProps>

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
    const { match, getProject } = this.props
    getProject(match.params.userName, match.params.projectName)
  }

  componentDidUpdate(prev: any) {
    const {
      match,
      projectDetails,
      getWorkspaces,
      newWorkspace,
      workspaces
    } = this.props
    if (prev.projectDetails.id !== projectDetails.id) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
    if (prev.newWorkspace !== newWorkspace) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
    if (workspaces.status !== prev.workspaces.status) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
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
              <AsyncWorkspaceTable />
            )}
          </Fragment>
        ) : (
          <Fragment />
        )}
      </Fragment>
    )
  }
}

const mapStateToProps = ({ project }:StoreState):WorkspacesMapStateToProps => ({
  workspaces: project.workspaces.servers.workspaces,
  newWorkspace: project.workspaces.add.newWorkspace,
  projectDetails: project.details.projectDetails,
})

const mapDispatchToProps = (dispatch: Dispatch):WorkspacesMapDispatchToProps =>
  bindActionCreators(
    {
    getProject,
    getWorkspaces
    },
    dispatch
  )


export default
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(withRouter(Workspaces))
