import React from 'react'
import { withRouter, Switch, Route, Redirect, RouteComponentProps } from 'react-router-dom'
import Loadable from 'react-loadable'
import {
  VerticalNavLayout,
  VerticalNavLayoutMenu,
  VerticalNavLayoutContent,
  VerticalNavMenu
} from '../../../components/VerticalNav'

interface SettingsRouterProps {
  url: string,
  path: string
}

interface SettingsProps extends RouteComponentProps<SettingsRouterProps> {
  projectDetails: any
}

const AsyncProjectDetails = Loadable({
  loader: () => import('./ProjectDetails'),
  loading: () => <div />
})
const AsyncAdvancedSettings = Loadable({
  loader: () => import('./AdvancedSettings'),
  loading: () => <div />
})

const Settings = (props: SettingsProps) => {
  const { match, projectDetails } = props
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
            render={() => (
              <AsyncProjectDetails />
            )}
            exact
          />
          <Route
            path={`${match.path}/advanced`}
            render={() => (
              <AsyncAdvancedSettings projectDetails={projectDetails} />
            )}
          />
          <Redirect from={`${match.url}`} to={`${match.url}/details`} />
        </Switch>
      </VerticalNavLayoutContent>
    </VerticalNavLayout>
  )
}

export default withRouter(Settings)
