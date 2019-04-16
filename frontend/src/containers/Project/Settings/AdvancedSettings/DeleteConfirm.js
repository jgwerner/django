import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import Modal from 'components/Modal'
import Text from 'components/atoms/Text'
import Button from 'components/atoms/Button'
import * as SettingsActions from '../actions'

const DeleteConfirm = props => {
  const { match, projectDetails, deleteProject } = props
  return (
    <React.Fragment>
      <Modal
        header="Delete project"
        body={
          <Fragment>
            <Text m={3}>Are you sure you want to delete this project?</Text>
            <Button
              ml="auto"
              variation="danger"
              onClick={() =>
                deleteProject(match.params.userName, projectDetails.id)
              }
            >
              Confirm
            </Button>
          </Fragment>
        }
      />
    </React.Fragment>
  )
}

const mapStateToProps = state => ({
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...SettingsActions
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(DeleteConfirm)
)
