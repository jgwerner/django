import styled from 'styled-components/macro'
import { color, fontWeight, space, textAlign } from 'styled-system'
import theme from 'utils/theme'

const size = props => {
  switch (props.size) {
    case 'h1':
      return {
        fontSize: `${theme.fontSizes[7]}px`
      }
    case 'h2':
      return {
        fontSize: `${theme.fontSizes[6]}px`
      }
    case 'h3':
      return {
        fontSize: `${theme.fontSizes[5]}px`
      }
    case 'h4':
      return {
        fontSize: `${theme.fontSizes[4]}px`
      }
    case 'h5':
      return {
        fontSize: `${theme.fontSizes[3]}px`
      }
    default:
      return 'h1'
  }
}

const bold = props =>
  props.bold
    ? {
        fontWeight: 'bold'
      }
    : null

const medium = props =>
  props.medium
    ? {
        fontWeight: '500'
      }
    : null

const sub = props =>
  props.sub
    ? {
        textTransform: 'uppercase',
        fontSize: `${theme.fontSizes[2]}px`
      }
    : null

const Heading = styled.div(
  color,
  fontWeight,
  space,
  textAlign,
  size,
  bold,
  medium,
  sub
)

Heading.displayName = 'Heading'

Heading.defaultProps = {
  color: 'gray10',
  size: 'h1',
  my: 2
}

export default Heading
