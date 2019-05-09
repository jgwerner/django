import React from 'react'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormError,
  FormButton
} from '../../../../components/Form'

interface AddWorkspaceFormProps {
  input: string
  label: string
  type: string
  placeholder?: string
  meta: any
  touched: boolean
  error: string
}

const required = (value: string) =>
  value || typeof value === 'string'
    ? undefined
    : 'A workspace name is required'

const renderField = ({
  input,
  label,
  type,
  meta: { touched, error }
}: AddWorkspaceFormProps) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const AddWorkspaceForm = (props: InjectedFormProps) => {
  const { handleSubmit, invalid } = props
  return (
    <React.Fragment>
      <Form m={2} onSubmit={handleSubmit}>
        <Field
          name="name"
          label="Name"
          component={renderField}
          type="text"
          validate={required}
        />
        <FormButton type="submit" my={2} disabled={invalid}>
          Submit
        </FormButton>
      </Form>
    </React.Fragment>
  )
}

export default reduxForm({
  form: 'addWorkspace'
})(AddWorkspaceForm)
