import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { withRouter, Route, RouteComponentProps } from 'react-router-dom'
import { TabbedNav, TabbedNavLink } from 'components/TabbedNav'
import {
  ContentTop,
  ContentTopAction
} from 'components/AuthenticatedLayout/Content'
import Container from 'components/atoms/Container'
import Button from 'components/atoms/Button'
import Loadable from 'react-loadable'
import Link from 'components/atoms/Link'
import { getUserInfo } from './actions'
import { StoreState } from 'utils/store'

interface HomeMapStateToProps {
  profileInfoFetched: boolean
}

interface HomeMapDispatchToProps {
  getUserInfo: () => void
}

type HomeProps = HomeMapStateToProps &
  HomeMapDispatchToProps &
  RouteComponentProps

const AsyncAddProject = Loadable({
  loader: () => import('./AddProject'),
  loading: () => <div />
})

const AsyncProjectList = Loadable({
  loader: () => import('./ProjectList'),
  loading: () => <div />
})

const Home = class extends React.PureComponent<HomeProps> {
  componentDidMount() {
    const { getUserInfo, profileInfoFetched } = this.props
    if (!profileInfoFetched) {
      getUserInfo()
    }
  }

  render() {
    const { profileInfoFetched } = this.props
    return (
      <Container margin="auto" width="100%">
        {!profileInfoFetched ? (
          <Container />
        ) : (
          <Container>
            <ContentTop>
              <TabbedNav>
                <TabbedNavLink to="/">Your Projects</TabbedNavLink>
              </TabbedNav>
              <ContentTopAction>
                <Link to="/projects/new">
                  <Button>Add Project</Button>
                </Link>
              </ContentTopAction>
            </ContentTop>
            <AsyncProjectList />
            <Route path="/projects/new" render={() => <AsyncAddProject />} />
          </Container>
        )}
      </Container>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  profileInfoFetched: state.home.user.profileInfoFetched
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getUserInfo
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Home)
)
