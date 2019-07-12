import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { getFormValues } from 'redux-form'
import Heading from 'components/atoms/Heading'
import ProjectDetailsForm from './Form'
import {
  updateProject,
  UpdateProjectActions,
  closeError,
  closeSuccess
} from '../actions'
import { StoreState } from 'utils/store'
import Banner from 'components/Banner'
import { getProject } from '../../actions'
import Container from 'components/atoms/Container'

interface ProjectDetailsRouteProps {
  userName: string
  projectName: string
}

interface ProjectDetailsMapStateToProps {
  values: object
  projectDetails: any
  updateError: boolean
  updateSuccess: boolean
  errorMessage: string
  projectUpdated: boolean
  projectFetched: boolean
}

interface ProjectDetailsMapDispatchToProps {
  updateProject: (userName: string, id: string, values: object) => void
  getProject: (userName: string, projectName: string) => void
  closeError: () => void
  closeSuccess: () => void
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

  // componentDidMount() {
  //   const {projectDetails, match, getProject } = this.props
  //   if (projectDetails !== undefined) {
  //     getProject(match.params.userName, match.params.projectName)
  //   }
  // }

  // componentWillUnmount() {
  //   const { closeError, closeSuccess } = this.props
  //   console.log('unmounting')
  //   closeSuccess()
  //   closeError()
  // }

  displaySuccess() {
    const { updateSuccess, closeSuccess } = this.props
    if (updateSuccess) {
      return (
        <Container m={2} width={1 / 2}>
          <Banner
            success
            width={1}
            message="Project has been updated"
            action={() => closeSuccess()}
          />
        </Container>
      )
    }
    // setTimeout(() => closeSuccess(), 4000)
  }

  displayError() {
    const { updateError, closeError, errorMessage } = this.props
    if (updateError) {
      return (
        <Container m={2} width={1 / 2}>
          <Banner
            danger
            width={1}
            message={errorMessage}
            action={() => closeError()}
          />
        </Container>
      )
    }
    // setTimeout(() => closeError(), 4000)
  }

  render() {
    const { match, values, projectDetails, updateProject } = this.props
    return (
      <React.Fragment>
        <Heading bold>Project Details</Heading>
        {projectDetails !== undefined ? (
          <React.Fragment>
            {this.displayError()}
            {this.displaySuccess()}
            <ProjectDetailsForm
              onSubmit={() =>
                updateProject(match.params.userName, projectDetails.id, values)
              }
              initialValues={{
                name: match.params.projectName,
                // name: projectDetails.name,
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
  updateError: state.project.settings.updateError,
  updateSuccess: state.project.settings.updateSuccess,
  errorMessage: state.project.settings.errorMessage,
  projectUpdated: state.project.settings.projectUpdated,
  projectFetched: state.project.details.projectFetched
})

const mapDispatchToProps = (dispatch: Dispatch<UpdateProjectActions>) =>
  bindActionCreators(
    {
      updateProject,
      closeError,
      closeSuccess,
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
