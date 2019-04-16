import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import { getFormValues } from 'redux-form'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Divider from 'components/atoms/Divider'
import Loadable from 'react-loadable'
import * as OAuth2Actions from './actions'

const AsyncNewApp = Loadable({
  loader: () => import('./NewAppForm'),
  loading: () => <div />
})
const AsyncAppList = Loadable({
  loader: () => import('./AppList'),
  loading: () => <div />
})

const OAuth2 = props => {
  const { username, values, createApp } = props
  return (
    <Container width={1 / 2}>
      <Heading bold>Applications</Heading>
      <AsyncAppList />
      <Divider />
      <Heading size="h3" bold>
        New Application
      </Heading>
      <AsyncNewApp onSubmit={() => createApp(username, values.name)} />
    </Container>
  )
}

const mapStateToProps = state => ({
  values: getFormValues('newApp')(state),
  username: state.home.user.username
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...OAuth2Actions
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(OAuth2)
)
