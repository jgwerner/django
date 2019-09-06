import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { getFormValues } from 'redux-form'
import Heading from 'components/atoms/Heading'
import ProjectDetailsForm from './Form'
import { updateProject, UpdateProjectActions } from '../actions'
import { StoreState } from 'utils/store'
import { getProject } from '../../actions'

interface ProjectDetailsRouteProps {
  userName: string
  projectName: string
}

interface ProjectDetailsMapStateToProps {
  values: object
  projectDetails: any
  projectUpdated: boolean
  projectFetched: boolean
}

interface ProjectDetailsMapDispatchToProps {
  updateProject: (userName: string, id: string, values: object) => void
  getProject: (userName: string, projectName: string) => void
}

type ProjectDetailsProps = ProjectDetailsMapStateToProps &
  ProjectDetailsMapDispatchToProps &
  RouteComponentProps<ProjectDetailsRouteProps>

const ProjectDetails = class extends React.PureComponent<ProjectDetailsProps> {
  componentDidUpdate(prev: any) {
    const { match, projectUpdated, getProject } = this.props
    if (prev.projectUpdated !== projectUpdated) {
      getProject(match.params.userName, match.params.projectName)
    }
  }

  render() {
    const { match, values, projectDetails, updateProject } = this.props
    return (
      <React.Fragment>
        <Heading bold>Project Details</Heading>
        {projectDetails !== undefined ? (
          <React.Fragment>
            <ProjectDetailsForm
              onSubmit={() =>
                updateProject(match.params.userName, projectDetails.id, values)
              }
              initialValues={{
                name: match.params.projectName,
                description:
                  projectDetails !== undefined ? projectDetails.description : ''
              }}
            />
          </React.Fragment>
        ) : (
          <React.Fragment />
        )}
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('projectDetails')(state),
  projectDetails: state.project.details.projectDetails,
  projectUpdated: state.project.settings.projectUpdated,
  projectFetched: state.project.details.projectFetched
})

const mapDispatchToProps = (dispatch: Dispatch<UpdateProjectActions>) =>
  bindActionCreators(
    {
      updateProject,
      getProject
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ProjectDetails)
)
