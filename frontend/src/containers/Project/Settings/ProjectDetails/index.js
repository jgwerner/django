import React from 'react'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { getFormValues } from 'redux-form'
import Heading from 'components/atoms/Heading'
import ProjectDetailsForm from './Form'
import * as SettingsActions from '../actions'

const ProjectDetails = props => {
  const { match, values, projectDetails, updateProject } = props
  return (
    <React.Fragment>
      <Heading bold>Project Details</Heading>
      <ProjectDetailsForm
        onSubmit={() =>
          updateProject(match.params.userName, projectDetails.id, values)
        }
        initialValues={{
          name: projectDetails.name,
          description: projectDetails.description
        }}
        projectDetails={projectDetails}
      />
    </React.Fragment>
  )
}

const mapStateToProps = state => ({
  values: getFormValues('projectDetails')(state)
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
  )(ProjectDetails)
)
