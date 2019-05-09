import React from 'react'
import styled from 'styled-components/macro'
import {
  space,
  fontSize,
  width,
  SpaceProps,
  FontSizeProps,
  WidthProps
} from 'styled-system'
import Text from 'components/atoms/Text'
import Input from 'components/atoms/Input'
import Container from 'components/atoms/Container'
import Button from 'components/atoms/Button'
import theme from 'utils/theme'

interface FormProps extends SpaceProps, FontSizeProps, WidthProps {
  label?: string
  children?: JSX.Element | JSX.Element[] | string
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

const StyledLabel = styled(Text)`
  ${space}
  ${width}
`

export const Form = styled.form<FormProps>`
  ${space}
  ${width}
`

export const FormField = (props: FormProps) => (
  <Container p={[1, 2]} {...props} />
)

export const FieldLabel = (props: FormProps) => (
  <StyledLabel
    width={[1, 1, 1]}
    fontSize={4}
    bold
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

export const FormError = (props: FormProps) => (
  <Text m={2} ml={0} color="red" pl={3} textAlign="justify" {...props} />
)

export const FormButton = (props: any) => (
  <Container width={1} p={2} display="inline-block">
    <StyledButton my={2} {...props} />
  </Container>
)
