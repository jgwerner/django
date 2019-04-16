import styled from 'styled-components/macro'
import {
  color,
  fontSize,
  space,
  textAlign,
  verticalAlign,
  lineHeight
} from 'styled-system'

const caps = props =>
  props.caps
    ? {
        textTransform: 'uppercase'
      }
    : null

const bold = props =>
  props.bold
    ? {
        fontWeight: 'bold'
      }
    : null

const Text = styled.div(
  color,
  fontSize,
  space,
  textAlign,
  caps,
  bold,
  verticalAlign,
  lineHeight
)

Text.Span = Text.withComponent('span')

Text.displayName = 'Text'

Text.defaultProps = {
  fontSize: 3
}

export default Text
