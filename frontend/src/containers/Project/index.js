import React from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter, Switch, Route, Redirect } from 'react-router-dom'
import Loadable from 'react-loadable'
import { TabbedNav, TabbedNavLink } from 'components/TabbedNav'
import { ContentTop } from 'components/AuthenticatedLayout/Content'
import Container from 'components/atoms/Container'
import Breadcrumbs from './Breadcrumbs'
import * as ProjectActions from './actions'

const AsyncWorkspaces = Loadable({
  loader: () => import('./Workspaces'),
  loading: () => <div />
})
const AsyncSettings = Loadable({
  loader: () => import('./Settings'),
  loading: () => <div />
})

const Project = class extends React.PureComponent {
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
                render={() => (
                  <AsyncWorkspaces projectDetails={projectDetails} />
                )}
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

const mapStateToProps = state => ({
  projectDetails: state.project.details.projectDetails,
  projectFetched: state.project.details.projectFetched
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...ProjectActions
    },
    dispatch
  )

Project.propTypes = {
  projectFetched: PropTypes.bool.isRequired,
  projectDetails: PropTypes.shape({
    private: PropTypes.bool.isRequired
  }).isRequired,
  getProject: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      id: PropTypes.node
    }).isRequired
  }).isRequired
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Project)
)
