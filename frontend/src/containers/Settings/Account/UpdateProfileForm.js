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

const required = value => (value ? undefined : 'An email address is required')

const email = value =>
  value && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value)
    ? 'Invalid email address'
    : undefined

const renderField = ({ input, label, type, meta: { touched, error } }) => (
  <FormField>
    <Flex>
      <FieldLabel py={0} width={1 / 3}>
        {label}
      </FieldLabel>
      <Container width={2 / 3}>
        <FormInput {...input} type={type} placeholder={label} />
        {touched && (error && <FormError>{error}</FormError>)}
      </Container>
    </Flex>
  </FormField>
)

const UpdateProfileForm = props => {
  const { handleSubmit, invalid, pristine } = props
  return (
    <Form mx={3} mt={4} width={1 / 2} onSubmit={handleSubmit}>
      <Field
        name="firstName"
        label="First Name"
        component={renderField}
        type="text"
      />
      <Field
        name="lastName"
        label="Last Name"
        component={renderField}
        type="text"
      />
      <Field
        name="email"
        label="Email"
        component={renderField}
        type="text"
        validate={[email, required]}
      />
      <FormButton type="submit" disabled={invalid || pristine}>
        Update Profile
      </FormButton>
    </Form>
  )
}

export default reduxForm({
  form: 'updateProfile',
  enableReinitialize: true
})(UpdateProfileForm)
