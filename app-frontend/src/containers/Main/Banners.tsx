import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { default as BannerComponent } from 'components/Banner'
import { StoreState } from 'utils/store'
import {
  closePasswordError,
  closePasswordSuccess
} from '../Settings/Account/actions'
import {
  closeCreateAppSuccess,
  closeCreateAppError,
  closeDeleteAppSuccess,
  closeDeleteAppError
} from '../Settings/OAuth2/actions'
import {
  closeUpdateProjectSuccess,
  closeUpdateProjectError,
  closeDeleteProjectSuccess,
  closeDeleteProjectError
} from '../Project/Settings/actions'
import { closeCreateProjectSuccess } from '../Home/AddProject/actions'
import { closeServerError } from '../Project/ProjectWorkspaces/actions'
import styled from 'styled-components'

const Banner = styled(BannerComponent)`
  margin: 5px 0;
  width: 100%;
`

interface BannersMapStateToProps {
  createProjectSuccess: boolean
  passwordUpdateSuccess: boolean
  passwordUpdateError: boolean
  createAppSuccess: boolean
  createAppError: boolean
  deleteAppSuccess: boolean
  deleteAppError: boolean
  updateProjectSuccess: boolean
  updateProjectError: boolean
  updateProjectErrorMessage: string
  deleteProjectError: boolean
  deleteProjectSuccess: boolean
  startServerError: boolean
}

interface BannersMapDispatchToProps {
  closeCreateProjectSuccess: () => void
  closeUpdateProjectSuccess: () => void
  closeUpdateProjectError: () => void
  closeDeleteProjectSuccess: () => void
  closeDeleteProjectError: () => void
  closeServerError: () => void
  closePasswordSuccess: () => void
  closePasswordError: () => void
  closeCreateAppSuccess: () => void
  closeCreateAppError: () => void
  closeDeleteAppSuccess: () => void
  closeDeleteAppError: () => void
}

type BannersProps = BannersMapStateToProps & BannersMapDispatchToProps

const Banners = class extends React.PureComponent<BannersProps> {
  render() {
    const {
      createProjectSuccess,
      closeCreateProjectSuccess,
      updateProjectSuccess,
      updateProjectError,
      updateProjectErrorMessage,
      closeUpdateProjectSuccess,
      closeUpdateProjectError,
      deleteProjectSuccess,
      deleteProjectError,
      closeDeleteProjectError,
      closeDeleteProjectSuccess,
      startServerError,
      closeServerError,
      passwordUpdateSuccess,
      passwordUpdateError,
      closePasswordSuccess,
      closePasswordError,
      createAppSuccess,
      createAppError,
      deleteAppSuccess,
      deleteAppError,
      closeCreateAppSuccess,
      closeCreateAppError,
      closeDeleteAppSuccess,
      closeDeleteAppError
    } = this.props
    return (
      <React.Fragment>
        {createProjectSuccess ? (
          <Banner
            success
            message="New project created"
            action={() => closeCreateProjectSuccess()}
          />
        ) : (
          ''
        )}

        {updateProjectSuccess ? (
          <Banner
            success
            message="Project updated"
            action={() => closeUpdateProjectSuccess()}
          />
        ) : (
          ''
        )}
        {updateProjectError ? (
          <Banner
            danger
            message={updateProjectErrorMessage}
            action={() => closeUpdateProjectError()}
          />
        ) : (
          ''
        )}
        {deleteProjectSuccess ? (
          <Banner
            success
            message="Project deleted"
            action={() => closeDeleteProjectSuccess()}
          />
        ) : (
          ''
        )}
        {deleteProjectError ? (
          <Banner
            danger
            message="There was an error deleting the project"
            action={() => closeDeleteProjectError()}
          />
        ) : (
          ''
        )}
        {startServerError ? (
          <Banner
            danger
            message="The server could not be found. Please delete the server and create a new one."
            action={() => closeServerError()}
          />
        ) : (
          ''
        )}
        {passwordUpdateSuccess ? (
          <Banner
            success
            message="Password Updated"
            action={() => closePasswordSuccess()}
          />
        ) : (
          ''
        )}
        {passwordUpdateError ? (
          <Banner
            danger
            message="There was an error updating your password"
            action={() => closePasswordError()}
          />
        ) : (
          ''
        )}
        {createAppSuccess ? (
          <Banner
            success
            width={1}
            message="New application created"
            action={() => closeCreateAppSuccess()}
          />
        ) : (
          ''
        )}
        {createAppError ? (
          <Banner
            danger
            width={1}
            message="Error creating new app"
            action={() => closeCreateAppError()}
          />
        ) : (
          ''
        )}
        {deleteAppSuccess ? (
          <Banner
            success
            width={1}
            message="Application has been deleted"
            action={() => closeDeleteAppSuccess()}
          />
        ) : (
          ''
        )}
        {deleteAppError ? (
          <Banner
            danger
            width={1}
            message="Error deleting app"
            action={() => closeDeleteAppError()}
          />
        ) : (
          ''
        )}
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  createProjectSuccess: state.home.addProject.createProjectSuccess,
  passwordUpdateSuccess: state.settings.account.passwordUpdateSuccess,
  passwordUpdateError: state.settings.account.passwordUpdateError,
  createAppSuccess: state.settings.oauth2.createAppSuccess,
  createAppError: state.settings.oauth2.createAppError,
  deleteAppSuccess: state.settings.oauth2.deleteAppSuccess,
  deleteAppError: state.settings.oauth2.deleteAppError,
  updateProjectSuccess: state.project.settings.updateProjectSuccess,
  updateProjectError: state.project.settings.updateProjectError,
  updateProjectErrorMessage: state.project.settings.updateProjectErrorMessage,
  deleteProjectSuccess: state.project.settings.deleteProjectSuccess,
  deleteProjectError: state.project.settings.deleteProjectError,
  startServerError: state.project.workspaces.servers.startServerError
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      closeCreateProjectSuccess,
      closePasswordSuccess,
      closePasswordError,
      closeCreateAppSuccess,
      closeCreateAppError,
      closeDeleteAppSuccess,
      closeDeleteAppError,
      closeUpdateProjectSuccess,
      closeUpdateProjectError,
      closeDeleteProjectError,
      closeDeleteProjectSuccess,
      closeServerError
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Banners)
