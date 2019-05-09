import styled from 'styled-components/macro'
import {
  color,
  fontSize,
  space,
  textAlign,
  verticalAlign,
  lineHeight,
  ColorProps,
  FontSizeProps,
  SpaceProps,
  TextAlignProps,
  VerticalAlignProps,
  LineHeightProps
} from 'styled-system'

export interface TextProps
  extends ColorProps,
    FontSizeProps,
    SpaceProps,
    TextAlignProps,
    VerticalAlignProps,
    LineHeightProps {
  caps?: boolean
  bold?: boolean
}

interface CapsProps extends TextProps {
  textTransform?: string
}

interface BoldProps extends TextProps {
  fontWeight?: number | string
}

const caps = (props: CapsProps) =>
  props.caps ? `text-transform: uppercase;` : null

const bold = (props: BoldProps) =>
  props.bold
    ? {
        fontWeight: 600
      }
    : null

const Text = styled.div<TextProps>(
  color,
  fontSize,
  space,
  textAlign,
  caps,
  bold,
  verticalAlign,
  lineHeight
)

export const TextSpan = Text.withComponent('span')

Text.displayName = 'Text'

Text.defaultProps = {
  fontSize: 3
}

export default Text
