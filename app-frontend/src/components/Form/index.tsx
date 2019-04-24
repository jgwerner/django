import React from 'react'
import PropTypes from 'prop-types'
import styled from 'styled-components/macro'
import { space, fontSize, width, SpaceProps, FontSizeProps, WidthProps } from 'styled-system'
import Text from '../../components/atoms/Text'
import Input from '../../components/atoms/Input'
import Container from '../../components/atoms/Container'
import Button from '../atoms/Button'
import theme from '../../utils/theme'


interface FormProps extends SpaceProps, FontSizeProps, WidthProps {
  label?: string
}

const StyledTextArea = styled.textarea<FormProps>(
  {
    border: `0.08rem solid ${theme.colors.gray7}`,
    width: '100%',
    height: '200px',
    borderRadius: 4,
    resize: 'none',
    outline: 'none',
    '&::placeholder': {
      color: `${theme.colors.gray7}`
    }
  },
  space,
  width,
  fontSize
)

const Radio = styled.input.attrs({
  type: 'radio'
})`
  float: left;
`
const StyledRadio = styled(Radio)<FormProps>`
  ${space}
`

const StyledButton = styled(Button)`
  float: right;
`
const StyledInput = styled(Input)<FormProps>`
  ${width}
`
const StyledLabel = styled(Text)<FormProps>`
  ${space}
  ${width}
`

export const Form = styled.form<FormProps>`
  ${space}
  ${width}
`
export const FormField = (props: any) => <Container p={[1, 2]} {...props} />

export const FieldLabel = (props: any) => (
  <StyledLabel
    width={[1, 1, 1]}
    fontSize={4}
    fontWeight={600}
    textAlign="left"
    py={3}
    {...props}
  />
)

export const FormInput = (props: any) => <StyledInput {...props} />

export const FormTextArea = (props: any) => (
  <StyledTextArea p={2} pl={3} width={1} fontSize={3} {...props} />
)

export const FormRadio = (props: any) => {
  const { label } = props
  return (
    <Text textAlign="justify" lineHeight={2}>
      <StyledRadio m={2} {...props} />
      {label}
    </Text>
  )
}

FormRadio.propTypes = {
  label: PropTypes.string.isRequired
}

export const FormError = (props: any) => (
  <Text m={2} ml={0} color="red" pl={3} textAlign="justify" {...props} />
)

export const FormButton = (props: any) => (
  <Container width={1} p={2} display="inline-block">
    <StyledButton my={2} {...props} />
  </Container>
)
