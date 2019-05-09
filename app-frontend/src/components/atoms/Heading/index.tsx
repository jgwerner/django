import styled from 'styled-components/macro'
import {
  color,
  space,
  textAlign,
  ColorProps,
  SpaceProps,
  TextAlignProps
} from 'styled-system'
import theme from 'utils/theme'

interface HeadingProps extends ColorProps, SpaceProps, TextAlignProps {
  size?: string
  bold?: boolean
  medium?: boolean
  sub?: boolean
}

const size = (props: HeadingProps) => {
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

const bold = (props: HeadingProps) =>
  props.bold
    ? {
        fontWeight: 600
      }
    : null

const medium = (props: HeadingProps) =>
  props.medium
    ? {
        fontWeight: 500
      }
    : null

const sub = (props: HeadingProps) =>
  props.sub
    ? `text-transform: uppercase;
      font-size: ${theme.fontSizes[2]}px;
      `
    : null

const Heading = styled.div<HeadingProps>(
  color,
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
