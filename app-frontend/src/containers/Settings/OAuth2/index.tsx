import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import { getFormValues } from 'redux-form'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Divider from 'components/atoms/Divider'
import Loadable from 'react-loadable'
import { createApp } from './actions'
import { StoreState } from 'utils/store'
import ErrorBoundary from 'utils/ErrorBoundary'

interface OAuth2MapStateToProps {
  username: string
  values: any
}

interface OAuth2MapDispatchToProps {
  createApp: (username: string, values: any) => void
}

type OAuth2Props = OAuth2MapStateToProps & OAuth2MapDispatchToProps

const AsyncNewApp = Loadable({
  loader: () => import('./NewAppForm'),
  loading: () => <div />
})
const AsyncAppList = Loadable({
  loader: () => import('./AppList'),
  loading: () => <div />
})

const OAuth2 = (props: OAuth2Props) => {
  const { username, values, createApp } = props
  return (
    <Container width={[1, 2 / 3, 1 / 2]}>
      <Heading bold>Applications</Heading>
      <ErrorBoundary>
        <AsyncAppList />
      </ErrorBoundary>
      <Divider />
      <Heading size="h3" bold>
        New Application
      </Heading>
      <ErrorBoundary>
        <AsyncNewApp onSubmit={() => createApp(username, values.name)} />
      </ErrorBoundary>
    </Container>
  )
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('newApp')(state),
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      createApp
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(OAuth2)
