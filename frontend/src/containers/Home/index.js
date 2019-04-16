import React from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter, Route } from 'react-router-dom'
import { TabbedNav, TabbedNavLink } from 'components/TabbedNav'
import {
  ContentTop,
  ContentTopAction
} from 'components/AuthenticatedLayout/Content'
import Container from 'components/atoms/Container'
import Button from 'components/atoms/Button'
import Loadable from 'react-loadable'
import Link from 'components/atoms/Link'
import * as HomeActions from './actions'

const AsyncAddProject = Loadable({
  loader: () => import('./AddProject'),
  loading: () => <div />
})

const AsyncProjectList = Loadable({
  loader: () => import('./ProjectList'),
  loading: () => <div />
})

const Home = class extends React.PureComponent {
  componentDidMount() {
    const { getUserInfo, profileInfoFetched } = this.props
    if (!profileInfoFetched) {
      getUserInfo()
    }
  }

  render() {
    const { username, profileInfoFetched } = this.props
    return (
      <Container m="auto" width="100%">
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
            <AsyncProjectList username={username} />
            <Route
              path="/projects/new"
              render={() => <AsyncAddProject username={username} />}
            />
          </Container>
        )}
      </Container>
    )
  }
}

const mapStateToProps = state => ({
  username: state.home.user.username,
  profileInfoFetched: state.home.user.profileInfoFetched
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...HomeActions
    },
    dispatch
  )

Home.propTypes = {
  username: PropTypes.string.isRequired,
  profileInfoFetched: PropTypes.bool.isRequired,
  getUserInfo: PropTypes.func.isRequired
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Home)
)
