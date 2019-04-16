import React from 'react'
import { Field, reduxForm } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormError,
  FormButton
} from 'components/Form'
import Flex from 'components/atoms/Flex'
import Container from 'components/atoms/Container'

const required = value =>
  value || typeof value === 'string' ? undefined : 'Required'

const minLength = value =>
  value && value.length < 8 ? `Must be 8 characters or more` : undefined

const matchPassword = (value, allValues) =>
  value !== allValues.password ? 'Passwords do not match' : undefined

const renderField = ({ input, label, type, meta: { touched, error } }) => (
  <FormField>
    <Flex>
      <FieldLabel py={0} width={1 / 2}>
        {label}
      </FieldLabel>
      <Container width={2 / 3}>
        <FormInput {...input} type={type} placeholder={label} />
        {touched && (error && <FormError>{error}</FormError>)}
      </Container>
    </Flex>
  </FormField>
)

const ChangePasswordForm = props => {
  const { handleSubmit, invalid, registering } = props
  return (
    <Form mx={3} width={1 / 2} onSubmit={handleSubmit}>
      <Field
        name="password"
        label="New Password"
        component={renderField}
        type="password"
        validate={[required, minLength]}
      />
      <Field
        name="confirmPassword"
        label="Confirm Password"
        component={renderField}
        type="password"
        validate={[required, matchPassword]}
      />
      <FormButton type="submit" disabled={invalid}>
        {registering ? '...' : 'Submit'}
      </FormButton>
    </Form>
  )
}

export default reduxForm({
  form: 'changePassword'
})(ChangePasswordForm)
