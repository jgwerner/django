import React from 'react'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FormError,
  FormButton
} from '../../../components/Form'

interface RequestFormProps {
  input?: string,
  label?: string,
  type?: string,
  meta?: any,
  touched?: boolean,
  error?: string,
}

const required = (value: string) =>
  value || typeof value === 'string' ? undefined : 'Required'

const renderField = ({ input, label, type, meta: { touched, error } }: RequestFormProps) => (
  <FormField>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const RequestForm = (props: InjectedFormProps) => {
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

export default reduxForm({
  form: 'pwRequest'
})(RequestForm)
