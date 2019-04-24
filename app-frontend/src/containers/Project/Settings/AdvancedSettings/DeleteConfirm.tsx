import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { bindActionCreators, Dispatch } from 'redux'
import Modal from '../../../../components/Modal'
import Text from '../../../../components/atoms/Text'
import Button from '../../../../components/atoms/Button'
import { deleteProject, DeleteProjectActions } from '../actions'
import { StoreState } from '../../../../utils/store';

interface DeleteConfirmRouteProps {
  userName: string
}

interface DeleteConfirmMapStateToProps {
  projectDetails: any,
}

interface DeleteConfirmMapDispatchToProps {
  deleteProject: (userName: string, id: string) => void
}

type DeleteConfirmProps = DeleteConfirmMapStateToProps & DeleteConfirmMapDispatchToProps & RouteComponentProps<DeleteConfirmRouteProps>

const DeleteConfirm = (props: DeleteConfirmProps) => {
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

const mapStateToProps = (state: StoreState) => ({
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch<DeleteProjectActions>) =>
  bindActionCreators(
    {
    deleteProject
    },
    dispatch
  )


export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(DeleteConfirm)
)
