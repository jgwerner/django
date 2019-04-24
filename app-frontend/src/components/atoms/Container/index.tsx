import styled from 'styled-components/macro'
import { space, width, color, display, textAlign, SpaceProps, ColorProps, WidthProps, DisplayProps, TextAlignProps } from 'styled-system'

export interface ContainerProps extends SpaceProps, WidthProps, ColorProps, DisplayProps, TextAlignProps {
}

const Container = styled.div<ContainerProps>(space, color, width, display, textAlign)

Container.displayName = 'Container'

Container.defaultProps = {}

export default Container
