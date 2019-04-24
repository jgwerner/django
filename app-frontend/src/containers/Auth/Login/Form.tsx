import React from 'react'
import { connect } from 'react-redux'
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import {
  Form,
  FormField,
  FormInput,
  FormError,
  FormButton
} from '../../../components/Form'
import { StoreState } from '../../../utils/store';

interface RenderFieldProps {
  input?: string,
  label?: string,
  type?: string,
  meta?: any,
  touched?: boolean,
  error?: string,
}

interface LoginFormProps extends InjectedFormProps {
  loggingIn?: boolean
}

const required = (value: string) =>
  value || typeof value === 'string' ? undefined : 'Required'

const renderField = ({ input, label, type, meta: { touched, error } }: RenderFieldProps) => (
  <FormField>
    <FormInput {...input} type={type} placeholder={label} />
    {touched && (error && <FormError>{error}</FormError>)}
  </FormField>
)

const LoginForm = (props: LoginFormProps) => {
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
      <FormButton type="submit" width='100%' disabled={invalid}>
        {loggingIn ? '...' : 'Sign in'}
      </FormButton>
    </Form>
  )
}

const mapStateToProps = (state: StoreState) => ({
  loggingIn: state.auth.login.loggingIn
})


const LoginFormEx = reduxForm({
  form: 'login'
})(LoginForm)

export default connect(mapStateToProps, null)(LoginFormEx)