import styled from 'styled-components/macro'
import { space, width, color, display, textAlign } from 'styled-system'

const Container = styled.div(space, color, width, display, textAlign)

Container.displayName = 'Container'

Container.defaultProps = {}

export default Container
