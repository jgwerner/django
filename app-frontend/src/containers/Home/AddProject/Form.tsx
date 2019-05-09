import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, Dispatch } from 'redux'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FieldLabel,
  FormTextArea,
  FormRadio,
  FormError,
  FormButton
} from 'components/Form'
import { StoreState } from 'utils/store'
import Banner from 'components/Banner'
import { closeError, CloseErrorAction } from './actions'

interface AddProjectFormProps {
  input: string
  label: string
  type: string
  placeholder?: string
  meta: any
  touched: boolean
  error: string
}

interface FormMapDispatchProps {
  closeError: () => void
}

interface FormWrapperProps extends InjectedFormProps {
  newProjectError?: boolean
}

type FormProps = FormWrapperProps & FormMapDispatchProps

const required = (value: string) =>
  value || typeof value === 'string' ? undefined : 'Required'

const alphaNumeric = (value: string) =>
  value && /[^a-zA-Z0-9-_]/i.test(value)
    ? 'Can only include letters, numbers, underscores, or hyphens'
    : undefined

const renderField = ({
  input,
  label,
  type,
  meta: { touched, error }
}: AddProjectFormProps) => (
  <FormField>
    <FieldLabel>{label}</FieldLabel>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const renderRadio = ({
  input,
  label,
  type,
  meta: { touched, error }
}: AddProjectFormProps) => (
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

const AddProjectForm = (props: FormProps) => {
  const { handleSubmit, invalid, newProjectError, closeError } = props
  return (
    <React.Fragment>
      {newProjectError ? (
        <Banner
          danger
          width={1}
          message="Error creating new project"
          action={() => closeError()}
        />
      ) : (
        ''
      )}
      <Form m={2} onSubmit={handleSubmit}>
        <Field
          name="name"
          label="Project Name"
          component={renderField}
          type="text"
          validate={[required, alphaNumeric]}
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
        <FormButton type="submit" disabled={invalid}>
          Submit
        </FormButton>
      </Form>
    </React.Fragment>
  )
}

const mapStateToProps = (state: StoreState) => ({
  newProjectError: state.home.addProject.newProjectError
})

const mapDispatchToProps = (dispatch: Dispatch<CloseErrorAction>) =>
  bindActionCreators(
    {
      closeError
    },
    dispatch
  )

const AddProject = connect(
  mapStateToProps,
  mapDispatchToProps
)(AddProjectForm)

export default reduxForm({
  form: 'addProject'
})(AddProject)
