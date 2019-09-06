import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import { getFormValues } from 'redux-form'
import Modal from 'components/Modal'
import AddProjectForm from './Form'
import { addProject, closeCreateProjectError } from './actions'
import { StoreState } from 'utils/store'

interface AddProjectMapStateToProps {
  username: string
  values: any
}

interface AddProjectMapDispatchToProps {
  addProject: (username: string, values: any) => void
  closeCreateProjectError: () => void
}

type AddProjectProps = AddProjectMapStateToProps & AddProjectMapDispatchToProps

const AddProject = class extends React.PureComponent<AddProjectProps> {
  componentWillUnmount() {
    const { closeCreateProjectError } = this.props
    closeCreateProjectError()
  }
  render() {
    const { username, values, addProject } = this.props
    return (
      <React.Fragment>
        <Modal
          header="Add new project"
          body={
            <AddProjectForm onSubmit={() => addProject(username, values)} />
          }
        />
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('addProject')(state),
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      addProject,
      closeCreateProjectError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AddProject)
