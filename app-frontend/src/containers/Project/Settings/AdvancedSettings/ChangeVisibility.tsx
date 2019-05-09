import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import { bindActionCreators, Dispatch } from 'redux'
import Modal from '../../../../components/Modal'
import Text from '../../../../components/atoms/Text'
import Button from '../../../../components/atoms/Button'
import { changeVisibility, ChangeVisibilityActions } from '../actions'
import { StoreState } from '../../../../utils/store'

interface ChangeVisibilityRouteProps {
  userName: string
}

interface ChangeVisibilityMapStateToProps {
  projectDetails: any
}

interface ChangeVisibilityMapDispatchToProps {
  changeVisibility: (userName: string, id: string, priv: boolean) => void
}

type ChangeVisibilityProps = ChangeVisibilityMapStateToProps &
  ChangeVisibilityMapDispatchToProps &
  RouteComponentProps<ChangeVisibilityRouteProps>

const ChangeVisibility = (props: ChangeVisibilityProps) => {
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

const mapStateToProps = (state: StoreState) => ({
  projectDetails: state.project.details.projectDetails
})

const mapDispatchToProps = (dispatch: Dispatch<ChangeVisibilityActions>) =>
  bindActionCreators(
    {
      changeVisibility
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ChangeVisibility)
)
