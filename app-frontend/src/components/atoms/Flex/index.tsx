import styled from 'styled-components/macro'
import {
  space,
  width,
  color,
  alignItems,
  justifyContent,
  flexWrap,
  flexDirection,
  SpaceProps,
  WidthProps,
  AlignItemsProps,
  JustifyContentProps,
  FlexWrapProps,
  FlexDirectionProps
} from 'styled-system'

export interface FlexProps extends   SpaceProps,
WidthProps,
AlignItemsProps,
JustifyContentProps,
FlexWrapProps,
FlexDirectionProps {

}

const Flex = styled.div<FlexProps>`
  display: flex;
  ${space} ${width} ${color} ${alignItems} ${justifyContent} ${flexWrap} ${flexDirection};
`

Flex.defaultProps = {
  flexDirection: 'row'
}

Flex.displayName = 'Flex'

export default Flex
