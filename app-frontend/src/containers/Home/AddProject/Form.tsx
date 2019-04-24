import React from 'react'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import Button from '../../../components/atoms/Button'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormTextArea,
  FormRadio,
  FormError
} from '../../../components/Form'

interface AddProjectFormProps {
  input: string,
  label: string,
  type: string,
  placeholder?: string,
  meta: any,
  touched: boolean,
  error: string
}

const required = (value: string) =>
  value || typeof value === 'string' ? undefined : 'Required'

const renderField = ({ input, label, type, meta: { touched, error } }: AddProjectFormProps) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const renderRadio = ({ input, label, type, meta: { touched, error } }: AddProjectFormProps) => (
  <FormField>
    <FormRadio {...input} type={type} label={label} />
    {touched && (error && <div>{error}</div>)}
  </FormField>
)

const renderTextArea = ({
  input,
  label,
  type,
  placeholder,
  meta: { touched, error }
}: AddProjectFormProps) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormTextArea {...input} type={type} placeholder={placeholder} />
    {touched && (error && <div>{error}</div>)}
  </FormField>
)

const AddProjectForm = (props: InjectedFormProps) => {
  const { handleSubmit, invalid } = props
  return (
    <React.Fragment>
      <Form m={2} onSubmit={handleSubmit}>
        <Field
          name="name"
          label="Project Name"
          component={renderField}
          type="text"
          validate={required}
        />
        <Field
          name="description"
          label="Description (Optional)"
          component={renderTextArea}
          type="textarea"
          placeholder="Your project description..."
        />
        <Field
          name="private"
          value="true"
          label="Private"
          component={renderRadio}
          type="radio"
          checked
        />
        <Field
          name="private"
          value="false"
          label="Public"
          component={renderRadio}
          type="radio"
        />
        <Button type="submit" disabled={invalid}>
          Submit
        </Button>
      </Form>
    </React.Fragment>
  )
}

export default reduxForm({
  form: 'addProject'
})(AddProjectForm)
