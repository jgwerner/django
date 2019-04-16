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

const RequestForm = props => {
  const { handleSubmit, invalid } = props
  return (
    <Form m={3} onSubmit={handleSubmit}>
      <Field
        name="email"
        label="Email"
        component={renderField}
        type="text"
        validate={[required]}
      />
      <FormButton type="submit" width={1} disabled={invalid}>
        Submit
      </FormButton>
    </Form>
  )
}

RequestForm.propTypes = {
  ...propTypes
}

export default reduxForm({
  form: 'pwRequest'
})(RequestForm)
