import styled from 'styled-components/macro'
import { space, width, borders, borderRadius, color } from 'styled-system'

const type = props => {
  switch (props.type) {
    case 'basic':
      return {
        position: 'relative',
        minHeight: '300px'
      }
    case 'auth':
      return {
        position: 'relative',
        // width: '550px',
        height: '600px'
      }
    case 'contentFull':
      return {
        // width: '1040px',
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

const Card = styled.div(
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
