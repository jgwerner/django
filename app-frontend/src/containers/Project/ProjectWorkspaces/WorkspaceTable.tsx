import React, { Fragment } from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Table, { TableRow, TableHeader, TableData } from 'components/Table'
import Button from 'components/atoms/Button'
import Flex from 'components/atoms/Flex'
import {
  getWorkspaces,
  startServer,
  stopServer,
  deleteServer,
  updateStatus
} from './actions'
import { StoreState } from 'utils/store'
import Icon from 'components/Icon'
import theme from 'utils/theme'

interface WorkspaceTableRouteProps {
  userName: string
  projectName: string
}

interface WorkspaceTableMapStateToProps {
  projectDetails: any
  serverRunning: boolean
  username: string
  workspaces: any
  deleteServerSuccess: boolean
  newWorkspace: boolean
  serverStatus: string
  statusURL: string
}

interface WorkspaceTableMapDispatchToProps {
  getWorkspaces: (userName: string, projectName: string) => void
  startServer: (userName: string, name: string, id: string) => void
  stopServer: (userName: string, name: string, id: string) => void
  deleteServer: (userName: string, name: string, id: string) => void
  updateStatus: (status: string) => void
}

type WorkspaceTableProps = WorkspaceTableMapStateToProps &
  WorkspaceTableMapDispatchToProps &
  RouteComponentProps<WorkspaceTableRouteProps>

const WorkspaceTable = class extends React.PureComponent<WorkspaceTableProps> {
  socket: WebSocket
  constructor(props: WorkspaceTableProps) {
    super(props)
    this.socket = new WebSocket(props.statusURL)
    this.socket.addEventListener('message', function(event: any) {
      var object = JSON.parse(event.data)
      props.updateStatus(object.status)
    })
  }

  componentWillUnmount() {
    this.socket.close()
  }

  componentDidUpdate(prev: any) {
    const {
      match,
      getWorkspaces,
      projectDetails,
      deleteServerSuccess
    } = this.props
    if (deleteServerSuccess !== prev.deleteServerSuccess) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
  }

  render() {
    const {
      username,
      projectDetails,
      workspaces,
      startServer,
      stopServer,
      deleteServer
    } = this.props
    return (
      <Fragment>
        {projectDetails.id === workspaces[0].project ? (
          <Table>
            <thead>
              <TableRow>
                <TableHeader>Name</TableHeader>
                <TableHeader>Status</TableHeader>
                <TableHeader>Type</TableHeader>
                <TableHeader>Actions</TableHeader>
              </TableRow>
            </thead>
            <tbody>
              {workspaces.map((i: any) => (
                <TableRow striped key={i.id}>
                  <TableData>{i.name}</TableData>
                  <TableData>{i.status}</TableData>
                  <TableData>{i.config.type}</TableData>
                  <TableData>
                    {i.status === 'Running' ? (
                      <Flex>
                        <Button variation="borderless" size="icon">
                          <a
                            style={{
                              textDecoration: 'none',
                              color: theme.colors.link
                            }}
                            href={i.endpoint}
                            rel="noopener noreferrer"
                            target="_blank"
                          >
                            Launch
                          </a>
                        </Button>
                        <Button
                          variation="borderless"
                          size="icon"
                          color="primary"
                          onClick={() =>
                            stopServer(username, projectDetails.name, i.id)
                          }
                        >
                          Stop
                        </Button>
                        <Button
                          variation="borderless"
                          size="icon"
                          onClick={() =>
                            deleteServer(username, projectDetails.name, i.id)
                          }
                        >
                          <Icon
                            size="25"
                            type="delete"
                            color={theme.colors.danger}
                          />
                        </Button>
                      </Flex>
                    ) : (
                      <Flex>
                        <Button
                          variation="borderless"
                          color="primary"
                          size="icon"
                          onClick={() =>
                            startServer(username, projectDetails.name, i.id)
                          }
                        >
                          Start
                        </Button>
                        <Button
                          variation="icon"
                          color="danger"
                          onClick={() =>
                            deleteServer(username, projectDetails.name, i.id)
                          }
                        >
                          <Icon size="25" type="delete" />
                        </Button>
                      </Flex>
                    )}
                  </TableData>
                </TableRow>
              ))}
            </tbody>
          </Table>
        ) : (
          <Fragment />
        )}
      </Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  username: state.home.user.username,
  serverSizes: state.project.workspaces.servers.serverSizes,
  serverRunning: state.project.workspaces.servers.serverRunning,
  workspaces: state.project.workspaces.servers.workspaces,
  projectDetails: state.project.details.projectDetails,
  deleteServerSuccess: state.project.workspaces.servers.deleteServerSuccess,
  newWorkspace: state.project.workspaces.add.newWorkspace,
  serverStatus: state.project.workspaces.servers.serverStatus
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getWorkspaces,
      startServer,
      stopServer,
      deleteServer,
      updateStatus
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(WorkspaceTable)
)
