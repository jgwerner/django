import React from 'react'
import { Field, reduxForm, propTypes } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FormError,
  FormButton
} from 'components/Form'

const required = value =>
  value || typeof value === 'string' ? undefined : 'Required'
const minLength = value =>
  value && value.length < 8 ? `Must be 8 characters or more` : undefined
const matchPassword = (value, allValues) =>
  value !== allValues.password ? 'Passwords do not match' : undefined

const renderField = ({ input, label, type, meta: { touched, error } }) => (
  <div>
    <FormField>
      <FormInput {...input} type={type} placeholder={label} />
    </FormField>
    {touched && (error && <FormError>{error}</FormError>)}
  </div>
)

const ConfirmForm = props => {
  const { handleSubmit } = props
  return (
    <Form my={3} onSubmit={handleSubmit}>
      <Field
        name="password"
        label="New password"
        component={renderField}
        type="password"
        validate={[required, minLength]}
      />
      <Field
        name="passwordConfirm"
        label="Confirm new password"
        component={renderField}
        type="password"
        validate={[required, matchPassword]}
      />
      <FormButton type="submit">Submit</FormButton>
    </Form>
  )
}

ConfirmForm.propTypes = {
  ...propTypes
}

export default reduxForm({
  form: 'pwConfirm'
})(ConfirmForm)
