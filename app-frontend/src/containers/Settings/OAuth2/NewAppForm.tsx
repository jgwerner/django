import React from 'react'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormError,
  FormButton
} from '../../../components/Form'


interface RenderFieldProps {
  input: string,
  label: string,
  type: string,
  meta: any,
  touched: boolean,
  error: string,
  initialValues: any
}

const required = (value: string) =>
  value || typeof value === 'string'
    ? undefined
    : 'You must name your application'

const renderField = ({ input, label, type, meta: { touched, error } }: RenderFieldProps) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const NewApp = (props: InjectedFormProps) => {
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
