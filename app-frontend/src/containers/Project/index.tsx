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
import { TabbedNav, TabbedNavLink } from '../../components/TabbedNav'
import { ContentTop } from '../../components/AuthenticatedLayout/Content'
import Container from '../../components/atoms/Container'
import Breadcrumbs from './Breadcrumbs'
import { getProject } from './actions'
import { StoreState } from '../../utils/store'

interface ProjectRouterProps {
  userName: string
  projectName: string
}

interface ProjectMapStateToProps {
  projectDetails: any
  projectFetched: boolean
}

interface ProjectMapDispatchToProps {
  getProject: (userName: string, projectName: string) => void
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

  render() {
    const { projectFetched, match, projectDetails } = this.props
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
                render={() => <AsyncSettings projectDetails={projectDetails} />}
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
  projectDetails: state.project.details.projectDetails,
  projectFetched: state.project.details.projectFetched
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getProject
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Project)
)
