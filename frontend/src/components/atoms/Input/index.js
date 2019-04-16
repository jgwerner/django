import styled from 'styled-components'
import { space, width, fontSize } from 'styled-system'
import theme from 'utils/theme'

export const Input = styled.input(
  {
    border: `0.08rem solid ${theme.colors.gray7}`,
    borderRadius: 4,
    outline: 'none',
    '&::placeholder': {
      color: `${theme.colors.gray7}`
    }
  },
  space,
  width,
  fontSize
)

Input.displayName = 'Input'

Input.defaultProps = {
  p: 2,
  pl: 3,
  width: 1,
  fontSize: 3
}

export default Input
