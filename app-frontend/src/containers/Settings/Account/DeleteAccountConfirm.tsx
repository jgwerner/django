import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import Modal from 'components/Modal'
import Text from 'components/atoms/Text'
import { StoreState } from 'utils/store'
import { deleteAccount, DeleteAccountActions } from './actions'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FormButton,
  FormError
} from 'components/Form'

interface DeleteAccountFieldProps {
  input: string
  label: string
  type: string
  meta: any
  touched: boolean
  error: string
}

interface DeleteAccountConfirmMapStateToProps {
  accountID: string
}

interface DeleteAccountConfirmMapDispatchToProps extends InjectedFormProps {
  deleteAccount: (accountID: string) => void
}

type DeleteAccountConfirmProps = DeleteAccountConfirmMapStateToProps &
  DeleteAccountConfirmMapDispatchToProps

const matchConfirm = (value: string) =>
  value !== 'DELETE ME'
    ? `You must enter 'DELETE ME' in order to delete your account.`
    : undefined

const renderField = ({
  input,
  label,
  type,
  meta: { touched, error }
}: DeleteAccountFieldProps) => (
  <FormField>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const DeleteAccountConfirm = (props: DeleteAccountConfirmProps) => {
  const { accountID, handleSubmit, invalid, deleteAccount } = props
  return (
    <React.Fragment>
      <Modal
        header="Are you sure you wish to delete your account?"
        body={
          <Fragment>
            <Text m={3}>
              Type <b>DELETE ME</b> below to confirm account deletion
            </Text>
            <Text caps bold m={3} fontSize={2} color="danger">
              This cannot be undone
            </Text>
            <Form onSubmit={handleSubmit}>
              <Field
                name="confirm"
                label="DELETE ME"
                component={renderField}
                type="text"
                validate={matchConfirm}
              />
              <FormButton
                type="submit"
                disabled={invalid}
                ml="auto"
                variation="danger"
                onClick={() => deleteAccount(accountID)}
              >
                Confirm
              </FormButton>
            </Form>
          </Fragment>
        }
      />
    </React.Fragment>
  )
}

const mapStateToProps = (state: StoreState) => ({
  accountID: state.home.user.accountID
})

const mapDispatchToProps = (dispatch: Dispatch<DeleteAccountActions>) =>
  bindActionCreators(
    {
      deleteAccount
    },
    dispatch
  )

const DeleteAccountConfirmForm = connect(
  mapStateToProps,
  mapDispatchToProps
)(DeleteAccountConfirm)

export default reduxForm({
  form: 'deleteAccountConfirm'
})(DeleteAccountConfirmForm)
