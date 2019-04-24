import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import { getFormValues } from 'redux-form'
import Modal from '../../../components/Modal'
import AddProjectForm from './Form'
import { addProject } from './actions'
import { StoreState } from '../../../utils/store';

interface AddProjectMapStateToProps {
  username: string,
  values: any
}

interface AddProjectMapDispatchToProps {
  addProject: (username: string, values: any) => void
}

type AddProjectProps = AddProjectMapStateToProps & AddProjectMapDispatchToProps

const AddProject = (props: AddProjectProps) => {
  const { username, values, addProject } = props
  return (
    <React.Fragment>
      <Modal
        header="Add new project"
        body={<AddProjectForm onSubmit={() => addProject(username, values)} />}
      />
    </React.Fragment>
  )
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('addProject')(state),
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      addProject
    },
    dispatch
  )

export default
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(AddProject)
