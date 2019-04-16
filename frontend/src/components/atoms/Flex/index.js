import styled from 'styled-components/macro'
import {
  space,
  width,
  color,
  alignItems,
  justifyContent,
  flexWrap,
  flexDirection
} from 'styled-system'

const Flex = styled.div`
  display: flex;
  ${space} ${width} ${color} ${alignItems} ${justifyContent} ${flexWrap} ${flexDirection};
`

Flex.defaultProps = {
  flexDirection: 'row'
}

Flex.displayName = 'Flex'

export default Flex
