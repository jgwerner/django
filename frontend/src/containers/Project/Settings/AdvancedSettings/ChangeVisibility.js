import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import Modal from 'components/Modal'
import Text from 'components/atoms/Text'
import Button from 'components/atoms/Button'
import * as SettingsActions from '../actions'

const ChangeVisibility = props => {
  const { match, projectDetails, changeVisibility } = props
  return (
    <React.Fragment>
      <Modal
        header={projectDetails.private ? 'Make public' : 'Make private'}
        body={
          <Fragment>
            <Text m={3}>Are you sure you want to change the visibility?</Text>
            <Button
              ml="auto"
              onClick={() =>
                changeVisibility(
                  match.params.userName,
                  projectDetails.id,
                  !projectDetails.private
                )
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
  )(ChangeVisibility)
)
