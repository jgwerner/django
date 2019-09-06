import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import {
  withRouter,
  Switch,
  Route,
  Redirect,
  RouteComponentProps
} from 'react-router-dom'
import Loadable from 'react-loadable'
import { TabbedNav, TabbedNavLink } from 'components/TabbedNav'
import { ContentTop } from 'components/AuthenticatedLayout/Content'
import Container from 'components/atoms/Container'
import Breadcrumbs from './Breadcrumbs'
import { getProject } from './actions'
import { StoreState } from 'utils/store'
import {
  closeUpdateProjectError,
  closeUpdateProjectSuccess
} from './Settings/actions'

interface ProjectRouterProps {
  userName: string
  projectName: string
}

interface ProjectMapStateToProps {
  projectFetched: boolean
  projectUpdated: boolean
}

interface ProjectMapDispatchToProps {
  getProject: (userName: string, projectName: string) => void
  closeUpdateProjectError: () => void
  closeUpdateProjectSuccess: () => void
}

type ProjectProps = ProjectMapStateToProps &
  ProjectMapDispatchToProps &
  RouteComponentProps<ProjectRouterProps>

const AsyncWorkspaces = Loadable({
  loader: () => import('./ProjectWorkspaces'),
  loading: () => <div />
})
const AsyncSettings = Loadable({
  loader: () => import('./Settings'),
  loading: () => <div />
})

const Project = class extends React.PureComponent<ProjectProps> {
  componentDidMount() {
    const { match, getProject } = this.props
    getProject(match.params.userName, match.params.projectName)
  }

  componentDidUpdate(prev: any) {
    const { match, getProject } = this.props
    if (match.params.projectName !== prev.match.params.projectName) {
      getProject(match.params.userName, match.params.projectName)
    }
  }

  componentWillUnmount() {
    const { closeUpdateProjectError, closeUpdateProjectSuccess } = this.props
    closeUpdateProjectError()
    closeUpdateProjectSuccess()
  }

  render() {
    const { projectFetched, match } = this.props
    return (
      <React.Fragment>
        {!projectFetched ? (
          <Container />
        ) : (
          <Container width="100%">
            <Breadcrumbs {...match.params} />
            <ContentTop>
              <TabbedNav>
                <TabbedNavLink to={`${match.url}/workspaces`}>
                  Workspaces
                </TabbedNavLink>
                <TabbedNavLink to={`${match.url}/settings`}>
                  Settings
                </TabbedNavLink>
              </TabbedNav>
            </ContentTop>
            <Switch>
              <Route
                path={`${match.path}/workspaces`}
                render={() => <AsyncWorkspaces />}
              />
              <Route
                path={`${match.path}/settings`}
                render={() => <AsyncSettings />}
              />
              <Redirect
                from={`${match.path}`}
                to={`${match.path}/workspaces`}
              />
            </Switch>
          </Container>
        )}
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  projectFetched: state.project.details.projectFetched,
  projectUpdated: state.project.settings.projectUpdated
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getProject,
      closeUpdateProjectError,
      closeUpdateProjectSuccess
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Project)
)
