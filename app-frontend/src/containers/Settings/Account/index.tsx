import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { withRouter, Route, RouteComponentProps } from 'react-router-dom'
import { connect } from 'react-redux'
import { getFormValues } from 'redux-form'
import Container from 'components/atoms/Container'
import Heading from 'components/atoms/Heading'
import Divider from 'components/atoms/Divider'
import Text from 'components/atoms/Text'
import Button from 'components/atoms/Button'
import Loadable from 'react-loadable'
import {
  updateProfile,
  changePassword,
  closeProfileSuccess,
  closeProfileError,
  closePasswordSuccess,
  closePasswordError
} from './actions'
import { getUserInfo } from 'containers/Home/actions'
import { StoreState } from 'utils/store'
import Banner from 'components/Banner'
import history from 'utils/history'

interface AccountSettingsRouteProps {
  path: string
  url: string
}

interface AccountSettingsMapStateToProps {
  accountID: string
  profileValues: any
  pwValues: any
  firstName: string
  lastName: string
  email: string
  profileUpdateSuccess: boolean
  profileUpdateError: boolean
  passwordUpdateSuccess: boolean
  passwordUpdateError: boolean
}

interface AccountSettingsMapDispatchToProps {
  updateProfile: (accountID: string, profileValues: any) => void
  changePassword: (accountID: string, pwValues: any) => void
  getUserInfo: () => void
  closeProfileSuccess: () => void
  closeProfileError: () => void
  closePasswordSuccess: () => void
  closePasswordError: () => void
}

type AccountSettingsProps = AccountSettingsMapStateToProps &
  AccountSettingsMapDispatchToProps &
  RouteComponentProps<AccountSettingsRouteProps>

const AsyncChangePassword = Loadable({
  loader: () => import('./ChangePasswordForm'),
  loading: () => <div />
})
const AsyncUpdateProfile = Loadable({
  loader: () => import('./UpdateProfileForm'),
  loading: () => <div />
})

const AsyncDeleteAccountConfirm = Loadable({
  loader: () => import('./DeleteAccountConfirm'),
  loading: () => <div />
})

const Account = class extends React.PureComponent<AccountSettingsProps> {
  componentDidUpdate(prev: any) {
    const { getUserInfo, profileUpdateSuccess } = this.props
    if (profileUpdateSuccess !== prev.profileUpdateSuccess) {
      getUserInfo()
    }
  }
  render() {
    const {
      match,
      accountID,
      firstName,
      lastName,
      email,
      pwValues,
      profileValues,
      updateProfile,
      changePassword,
      profileUpdateSuccess,
      profileUpdateError,
      passwordUpdateSuccess,
      passwordUpdateError,
      closeProfileSuccess,
      closeProfileError,
      closePasswordSuccess,
      closePasswordError
    } = this.props
    return (
      <Container width={1}>
        {profileUpdateSuccess ? (
          <Banner
            success
            message="Profile updated"
            action={() => closeProfileSuccess()}
          />
        ) : (
          ''
        )}
        {profileUpdateError ? (
          <Banner
            danger
            message="There was an error updating your profile"
            action={() => closeProfileError()}
          />
        ) : (
          ''
        )}
        {passwordUpdateSuccess ? (
          <Banner
            success
            message="Password updated"
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
          Deleting your account will remove all your information from our
          system.
        </Text>
        <Button
          size="large"
          variation="danger"
          onClick={() => history.push(`${match.url}/delete/confirm`)}
        >
          Delete account
        </Button>
        <Route
          path={`${match.path}/delete/confirm`}
          render={() => <AsyncDeleteAccountConfirm />}
        />
      </Container>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  accountID: state.home.user.accountID,
  profileValues: getFormValues('updateProfile')(state),
  pwValues: getFormValues('changePassword')(state),
  firstName: state.home.user.firstName,
  lastName: state.home.user.lastName,
  email: state.home.user.email,
  profileUpdateSuccess: state.settings.account.profileUpdateSuccess,
  profileUpdateError: state.settings.account.profileUpdateError,
  passwordUpdateSuccess: state.settings.account.passwordUpdateSuccess,
  passwordUpdateError: state.settings.account.passwordUpdateError
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      updateProfile,
      changePassword,
      getUserInfo,
      closeProfileSuccess,
      closeProfileError,
      closePasswordSuccess,
      closePasswordError
    },
    dispatch
  )

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(Account)
)
