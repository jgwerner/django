import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import { getFormValues } from 'redux-form'
import Modal from '../../../../components/Modal'
import AddWorkspaceForm from './Form'
import { addWorkspace } from './actions'
import { StoreState } from '../../../../utils/store'

interface AddWorkspaceMapStateToProps {
  projectDetails: any
  username: string
  values: any
  server: string
}

interface AddWorkspaceMapDispatchToProps {
  addWorkspace: (
    username: string,
    server: any,
    projectID: string,
    values: any
  ) => void
}

type AddWorkspaceProps = AddWorkspaceMapStateToProps &
  AddWorkspaceMapDispatchToProps

const AddWorkspace = (props: AddWorkspaceProps) => {
  const { username, values, addWorkspace, projectDetails, server } = props
  return (
    <React.Fragment>
      <Modal
        header="Add new workspace"
        body={
          <AddWorkspaceForm
            onSubmit={() =>
              addWorkspace(username, server[0], projectDetails.id, values)
            }
          />
        }
      />
    </React.Fragment>
  )
}

const mapStateToProps = (state: StoreState) => ({
  values: getFormValues('addWorkspace')(state),
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      addWorkspace
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(AddWorkspace)
