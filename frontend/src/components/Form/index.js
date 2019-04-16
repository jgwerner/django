import React from 'react'
import styled from 'styled-components/macro'
import { space, fontSize, width } from 'styled-system'
import Text from 'components/atoms/Text'
import Input from 'components/atoms/Input'
import Container from 'components/atoms/Container'
import Button from 'components/atoms/Button'
import theme from 'utils/theme'

const StyledTextArea = styled.textarea(
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

const StyledRadio = styled.input.attrs({
  type: 'radio'
})`
  float: left;
  ${space}
`

const StyledButton = styled(Button)`
  float: right;
`
const StyledInput = styled(Input)`
  ${width}
`
const StyledLabel = styled(Text)`
  ${space}
  ${width}
`

export const Form = styled.form`
  ${space}
  ${width}
`
export const FormField = props => <Container p={[1, 2]} {...props} />

export const FieldLabel = props => (
  <StyledLabel
    width={[1, 1, 1]}
    fontSize={4}
    fontWeight={600}
    textAlign="left"
    py={3}
    {...props}
  />
)

export const FormInput = props => <StyledInput {...props} />

export const FormTextArea = props => (
  <StyledTextArea p={2} pl={3} width={1} fontSize={3} {...props} />
)

export const FormRadio = props => {
  const { label } = props
  return (
    <Text textAlign="justify" lineHeight={2}>
      <StyledRadio m={2} {...props} />
      {label}
    </Text>
  )
}

export const FormError = props => (
  <Text m={2} ml={0} color="red" pl={3} textAlign="justify" {...props} />
)

export const FormButton = props => (
  <Container width={1} p={2} display="inline-block">
    <StyledButton my={2} {...props} />
  </Container>
)
