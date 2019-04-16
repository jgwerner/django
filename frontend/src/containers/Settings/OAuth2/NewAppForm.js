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

const required = value =>
  value || typeof value === 'string'
    ? undefined
    : 'You must name your application'

const renderField = ({ input, label, type, meta: { touched, error } }) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const NewApp = props => {
  const { handleSubmit, invalid } = props
  return (
    <React.Fragment>
      <Form m={2} onSubmit={handleSubmit}>
        <Field
          name="name"
          label="App Name"
          component={renderField}
          type="text"
          validate={required}
        />
        <FormButton type="submit" my={2} disabled={invalid}>
          Create
        </FormButton>
      </Form>
    </React.Fragment>
  )
}

export default reduxForm({
  form: 'newApp'
})(NewApp)
