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

interface SettingsRouterProps {
  url: string
  path: string
}

type SettingsProps = RouteComponentProps<SettingsRouterProps>

const AsyncAccountSettings = Loadable({
  loader: () => import('./Account'),
  loading: () => <div />
})
const AsyncOAuth2Settings = Loadable({
  loader: () => import('./OAuth2'),
  loading: () => <div />
})

const Settings = (props: SettingsProps) => {
  const { match } = props
  return (
    <VerticalNavLayout>
      <VerticalNavLayoutMenu>
        <VerticalNavMenu
          links={[
            { to: `${match.url}/account`, children: 'Account', exact: true },
            { to: `${match.url}/oauth2`, children: 'Applications' }
          ]}
        />
      </VerticalNavLayoutMenu>
      <VerticalNavLayoutContent>
        <Switch>
          <Route
            path={`${match.path}/account`}
            render={() => <AsyncAccountSettings />}
          />
          <Route
            path={`${match.path}/oauth2`}
            render={() => <AsyncOAuth2Settings />}
          />
          <Redirect from={`${match.url}`} to={`${match.url}/account`} />
        </Switch>
      </VerticalNavLayoutContent>
    </VerticalNavLayout>
  )
}

export default withRouter(Settings)
