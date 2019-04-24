import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { getFormValues } from 'redux-form'
import Container from '../../../components/atoms/Container'
import Heading from '../../../components/atoms/Heading'
import Divider from '../../../components/atoms/Divider'
import Text from '../../../components/atoms/Text'
import Button from '../../../components/atoms/Button'
import Loadable from 'react-loadable'
import { updateProfile, changePassword } from './actions'
import { StoreState } from '../../../utils/store';

interface AccountSettingsMapStateToProps {
  accountID: string,
  profileValues: any,
  pwValues: any,
  firstName: string,
  lastName: string,
  email: string
}

interface AccountSettingsMapDispatchToProps {
  updateProfile: (accountID: string, profileValues: any) => void,
  changePassword: (accountID: string, pwValues: any) => void
}

type AccountSettingsProps = AccountSettingsMapStateToProps & AccountSettingsMapDispatchToProps 

const AsyncChangePassword = Loadable({
  loader: () => import('./ChangePasswordForm'),
  loading: () => <div />
})
const AsyncUpdateProfile = Loadable({
  loader: () => import('./UpdateProfileForm'),
  loading: () => <div />
})

const Account = (props: AccountSettingsProps) => {
  const {
    accountID,
    firstName,
    lastName,
    email,
    pwValues,
    profileValues,
    updateProfile,
    changePassword
  } = props
  return (
    <Container width={1}>
      <Heading my={4} bold size="h2">
        Profile Info
      </Heading>
      <AsyncUpdateProfile
        onSubmit={() => updateProfile(accountID, profileValues)}
        initialValues={{
          firstName,
          lastName,
          email
        }}
      />
      <Divider />
      <Heading my={4} bold size="h2">
        Change Password
      </Heading>
      <AsyncChangePassword
        onSubmit={() => changePassword(accountID, pwValues)}
      />
      <Divider />
      <Heading my={4} bold size="h2">
        Delete Account
      </Heading>
      <Text color="danger" bold mb={4}>
        WARNING! This cannot be undone.
      </Text>
      <Text mb={4}>
        Deleting your account will remove all your information from our system.
      </Text>
      <Button size="large" variation="danger">
        Delete account
      </Button>
    </Container>
  )
}

const mapStateToProps = (state: StoreState) => ({
  accountID: state.home.user.accountID,
  profileValues: getFormValues('updateProfile')(state),
  pwValues: getFormValues('changePassword')(state),
  firstName: state.home.user.firstName,
  lastName: state.home.user.lastName,
  email: state.home.user.email
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      updateProfile,
      changePassword
    },
    dispatch
  )

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Account)
