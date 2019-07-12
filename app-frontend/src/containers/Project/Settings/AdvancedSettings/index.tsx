import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { withRouter, Route, RouteComponentProps } from 'react-router-dom'
import Loadable from 'react-loadable'
import Heading from 'components/atoms/Heading'
import Text from 'components/atoms/Text'
import Flex from 'components/atoms/Flex'
import Button from 'components/atoms/Button'
import history from 'utils/history'
import { getProject } from '../../actions'
import { closeError, closeSuccess } from '../actions'
import { StoreState } from 'utils/store'
import Banner from 'components/Banner'

interface AdvancedSettingsRouteProps {
  userName: string
  projectName: string
}

interface AdvancedSettingsMapStateToProps {
  projectDetails: any
  updateError: boolean
  updateSuccess: boolean
  errorMessage: string
}

interface AdvancedSettingsMapDispatchToProps {
  getProject: (userName: string, projectName: string) => void
  closeError: () => void
  closeSuccess: () => void
}

type AdvancedSettingsProps = AdvancedSettingsMapStateToProps &
  AdvancedSettingsMapDispatchToProps &
  RouteComponentProps<AdvancedSettingsRouteProps>

const AsyncChangeVisibility = Loadable({
  loader: () => import('./ChangeVisibility'),
  loading: () => <div />
})

const AsyncDeleteConfirm = Loadable({
  loader: () => import('./DeleteConfirm'),
  loading: () => <div />
})

const AdvancedSettings = class extends React.PureComponent<
  AdvancedSettingsProps
> {
  componentDidMount() {
    const { closeError, closeSuccess } = this.props
    closeError()
    closeSuccess()
  }

  componentDidUpdate(prev: any) {
    const { match, projectDetails, getProject } = this.props
    if (prev.projectDetails.private !== projectDetails.private)
      getProject(match.params.userName, match.params.projectName)
  }

  componentWillUnmount() {
    const { closeError, closeSuccess } = this.props
    closeError()
    closeSuccess()
  }

  render() {
    const {
      match,
      projectDetails,
      updateError,
      updateSuccess,
      closeError,
      closeSuccess
    } = this.props
    return (
      <React.Fragment>
        <Heading mb={4} bold>
          Advanced Settings
        </Heading>
        {updateError ? (
          <Banner
            danger
            width={1}
            message="There was an error updating the project"
            action={() => closeError()}
          />
        ) : (
          ''
        )}
        {updateSuccess ? (
          <Banner
            success
            width={1}
            message="Project has been updated"
            action={() => closeSuccess()}
          />
        ) : (
          ''
        )}
        <Flex width="100%" m={[2, 3, 4]}>
          <Text m={2}>
            {projectDetails.private
              ? 'Make this project public'
              : 'Make this project private'}
          </Text>
          <Button
            ml="auto"
            size="large"
            onClick={() => history.push(`${match.url}/visibility`)}
          >
            {projectDetails.private ? 'Make public' : 'Make private'}
          </Button>
          <Route
            path={`${match.path}/visibility`}
            render={() => <AsyncChangeVisibility />}
          />
        </Flex>
        <Flex width="100%" m={[2, 3, 4]}>
          <Text m={2}>Delete project</Text>
          <Button
            ml="auto"
            variation="danger"
            size="large"
            onClick={() => history.push(`${match.url}/delete/confirm`)}
          >
            Delete
          </Button>
          <Route
            path={`${match.path}/delete/confirm`}
            render={() => <AsyncDeleteConfirm />}
          />
        </Flex>
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  projectDetails: state.project.details.projectDetails,
  updateError: state.project.settings.updateError,
  updateSuccess: state.project.settings.updateSuccess,
  errorMessage: state.project.settings.errorMessage
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getProject,
      closeError,
      closeSuccess
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(AdvancedSettings)
)
