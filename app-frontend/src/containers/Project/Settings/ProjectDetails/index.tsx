import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { getFormValues } from 'redux-form'
import Heading from '../../../../components/atoms/Heading'
import ProjectDetailsForm from './Form'
import { updateProject, UpdateProjectActions } from '../actions'
import { StoreState } from '../../../../utils/store'

interface ProjectDetailsRouteProps {
  userName: string
}

interface ProjectDetailsMapStateToProps {
  values: object
  projectDetails: any
}

interface ProjectDetailsMapDispatchToProps {
  updateProject: (userName: string, id: string, values: object) => void
}

type ProjectDetailsProps = ProjectDetailsMapStateToProps &
  ProjectDetailsMapDispatchToProps &
  RouteComponentProps<ProjectDetailsRouteProps>

const ProjectDetails = (props: ProjectDetailsProps) => {
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
      />
    </React.Fragment>
  )
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('projectDetails')(state),
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch<UpdateProjectActions>) =>
  bindActionCreators(
    {
      updateProject
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ProjectDetails)
)
