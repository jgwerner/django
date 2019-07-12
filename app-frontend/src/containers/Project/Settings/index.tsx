import React from 'react'
import {
  withRouter,
  Switch,
  Route,
  Redirect,
  RouteComponentProps
} from 'react-router-dom'
import Loadable from 'react-loadable'
import {
  VerticalNavLayout,
  VerticalNavLayoutMenu,
  VerticalNavLayoutContent,
  VerticalNavMenu
} from 'components/VerticalNav'
import { StoreState } from 'utils/store'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { getProject } from '../actions'

interface SettingsRouterProps {
  url: string
  path: string
  userName: string
  projectName: string
}

interface SettingsMapStateToProps {
  projectFetched: boolean
  projectUpdated: boolean
}

interface SettingsMapDispatchToProps {
  getProject: (userName: string, projectName: string) => void
}

type SettingsProps = SettingsMapStateToProps &
  SettingsMapDispatchToProps &
  RouteComponentProps<SettingsRouterProps>

const AsyncProjectDetails = Loadable({
  loader: () => import('./ProjectDetails'),
  loading: () => <div />
})
const AsyncAdvancedSettings = Loadable({
  loader: () => import('./AdvancedSettings'),
  loading: () => <div />
})

const Settings = class extends React.PureComponent<SettingsProps> {
  // componentDidMount() {
  //   const { match, getProject, projectUpdated } = this.props
  //   console.log('CDM')
  //   if (projectUpdated) {
  //   getProject(match.params.userName, match.params.projectName)
  //   }
  // }
  render() {
    const { match } = this.props
    return (
      <VerticalNavLayout project>
        <VerticalNavLayoutMenu>
          <VerticalNavMenu
            links={[
              {
                to: `${match.url}/details`,
                children: 'Project Details',
                exact: true
              },
              { to: `${match.url}/advanced`, children: 'Advanced Settings' }
            ]}
          />
        </VerticalNavLayoutMenu>
        <VerticalNavLayoutContent>
          <Switch>
            <Route
              path={`${match.path}/details`}
              render={() => <AsyncProjectDetails />}
              exact
            />
            <Route
              path={`${match.path}/advanced`}
              render={() => <AsyncAdvancedSettings />}
            />
            <Redirect from={`${match.url}`} to={`${match.url}/details`} />
          </Switch>
        </VerticalNavLayoutContent>
      </VerticalNavLayout>
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
      getProject
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Settings)
)
