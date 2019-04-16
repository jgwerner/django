import React from 'react'
import PropTypes from 'prop-types'
import { withRouter, Switch, Route, Redirect } from 'react-router-dom'
import Loadable from 'react-loadable'
import {
  VerticalNavLayout,
  VerticalNavLayoutMenu,
  VerticalNavLayoutContent,
  VerticalNavMenu
} from 'components/VerticalNav'

const AsyncProjectDetails = Loadable({
  loader: () => import('./ProjectDetails'),
  loading: () => <div />
})
const AsyncAdvancedSettings = Loadable({
  loader: () => import('./AdvancedSettings'),
  loading: () => <div />
})

const Settings = props => {
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
              <AsyncProjectDetails projectDetails={projectDetails} />
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

Settings.propTypes = {
  projectDetails: PropTypes.shape({}).isRequired,
  match: PropTypes.shape({
    url: PropTypes.string,
    path: PropTypes.string
  }).isRequired
}

export default withRouter(Settings)
