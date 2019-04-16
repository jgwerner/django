import React from 'react'
import { Field, reduxForm, propTypes } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormTextArea,
  FormError,
  FormButton
} from 'components/Form'

const required = value => (value ? undefined : 'This field cannot be blank')

const renderField = ({
  input,
  label,
  type,
  placeholder,
  meta: { touched, error }
}) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={placeholder} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const renderTextArea = ({ input, label, type, meta: { touched, error } }) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormTextArea {...input} type={type} placeholder={label} />
    {touched && (error && <div>{error}</div>)}
  </FormField>
)

const ProjectDetailsForm = props => {
  const { handleSubmit, invalid } = props
  return (
    <React.Fragment>
      <Form m={2} width={1 / 2} onSubmit={handleSubmit}>
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
        />
        <FormButton type="submit" disabled={invalid}>
          Save Changes
        </FormButton>
      </Form>
    </React.Fragment>
  )
}

ProjectDetailsForm.propTypes = {
  ...propTypes
}

export default reduxForm({
  form: 'projectDetails',
  enableReinitialize: true
})(ProjectDetailsForm)
