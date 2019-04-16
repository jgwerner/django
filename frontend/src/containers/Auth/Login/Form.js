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

const renderField = ({ input, label, type, meta: { touched, error } }) => (
  <FormField>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const LoginForm = props => {
  const { handleSubmit, invalid, loggingIn } = props
  return (
    <Form m={3} onSubmit={handleSubmit}>
      <Field
        name="username"
        label="Username"
        component={renderField}
        type="text"
        validate={[required]}
      />
      <Field
        name="password"
        label="Password"
        component={renderField}
        type="password"
        validate={required}
      />
      <FormButton type="submit" width={1} disabled={invalid}>
        {loggingIn ? '...' : 'Sign in'}
      </FormButton>
    </Form>
  )
}

LoginForm.propTypes = {
  ...propTypes
}

export default reduxForm({
  form: 'login'
})(LoginForm)
