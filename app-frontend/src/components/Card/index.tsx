import styled from 'styled-components/macro'
import {
  space,
  width,
  borders,
  borderRadius,
  color,
  SpaceProps,
  WidthProps,
  BordersProps,
  BorderRadiusProps,
  ColorProps
} from 'styled-system'

interface CardProps
  extends SpaceProps,
    WidthProps,
    BordersProps,
    BorderRadiusProps,
    ColorProps {
  type?: string
}

interface TypeProps extends CardProps {
  minHeight?: string
  height?: string
}

const type = (props: TypeProps) => {
  switch (props.type) {
    case 'basic':
      return {
        // position: 'relative',
        minHeight: '300px'
      }
    case 'auth':
      return {
        // position: 'relative',
        height: '600px'
      }
    case 'contentFull':
      return {
        minHeight: '700px'
      }
    case 'contentPartial':
      return {
        height: 'auto'
      }
    default:
      return 'basic'
  }
}

const Card = styled.div<CardProps>(
  {
    backgroundColor: 'white',
    border: '1px solid rgba(0, 0, 0, 0.15)',
    borderRadius: '4px'
  },
  space,
  width,
  borders,
  borderRadius,
  color,
  type
)

Card.displayName = 'Card'

Card.defaultProps = {
  type: 'contentFull'
}

export default Card
