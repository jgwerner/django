import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter, Route } from 'react-router-dom'
import Heading from 'components/atoms/Heading'
import Text from 'components/atoms/Text'
import Flex from 'components/atoms/Flex'
import Button from 'components/atoms/Button'
import history from 'utils/history'
import * as SettingsActions from '../actions'
import * as ProjectActions from '../../actions'
import DeleteConfirm from './DeleteConfirm'
import ChangeVisibility from './ChangeVisibility'

const AdvancedSettings = class extends React.PureComponent {
  componentDidUpdate(prev) {
    const { match, projectDetails, getProject } = this.props
    if (prev.projectDetails.private !== projectDetails.private)
      getProject(match.params.userName, match.params.projectName)
  }

  render() {
    const { match, projectDetails } = this.props
    return (
      <React.Fragment>
        <Heading mb={4} bold>
          Advanced Settings
        </Heading>
        <Flex width="100%" m={4}>
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
            render={() => <ChangeVisibility />}
          />
        </Flex>
        <Flex width="100%" m={4}>
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
            render={() => <DeleteConfirm />}
          />
        </Flex>
      </React.Fragment>
    )
  }
}

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...SettingsActions,
      ...ProjectActions
    },
    dispatch
  )

export default withRouter(
  connect(
    null,
    mapDispatchToProps
  )(AdvancedSettings)
)
