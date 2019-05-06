import React, { Fragment } from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Table, { TableRow, TableHeader, TableData } from '../../../components/Table'
import Button from '../../../components/atoms/Button'
import Flex from '../../../components/atoms/Flex'
import { getWorkspaces, startServer, stopServer } from './actions'
import { StoreState } from '../../../utils/store';

interface WorkspaceTableRouteProps {
  userName: string,
  projectName: string
}

interface WorkspaceTableMapStateToProps {
  projectDetails: any,
  serverRunning: boolean,
  username: string,
  workspaces: any,
}

interface WorkspaceTableMapDispatchToProps {
  getWorkspaces: (userName: string, projectName: string) => void,
  startServer: (userName: string, name: string, id: string) => void,
  stopServer: (userName: string, name: string, id: string) => void
}

type WorkspaceTableProps = WorkspaceTableMapStateToProps & WorkspaceTableMapDispatchToProps & RouteComponentProps<WorkspaceTableRouteProps>

const WorkspaceTable = class extends React.PureComponent<WorkspaceTableProps> {
  componentDidUpdate(prev: any) {
    const { match, getWorkspaces, projectDetails, serverRunning } = this.props
    if (serverRunning !== prev.serverRunning) {
      getWorkspaces(match.params.userName, projectDetails.id)
    }
  }

  render() {
    const {
      username,
      projectDetails,
      workspaces,
      startServer,
      stopServer
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
                        <Button>Launch</Button>
                        <Button
                          onClick={() =>
                            stopServer(username, projectDetails.name, i.id)
                          }
                          variation="danger"
                        >
                          Stop
                        </Button>
                      </Flex>
                    ) : (
                      <Button
                        onClick={() =>
                          startServer(username, projectDetails.name, i.id)
                        }
                      >
                        Start
                      </Button>
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
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getWorkspaces, startServer, stopServer
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(WorkspaceTable)
)