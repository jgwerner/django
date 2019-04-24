import styled from 'styled-components/macro'
import { space, SpaceProps, width, WidthProps } from 'styled-system'
import theme from '../../../utils/theme'

interface DividerProps extends SpaceProps, WidthProps {}

const Divider = styled.hr<DividerProps>`
  border: 0;
  border-bottom: 1px solid ${theme.colors.gray2};
  ${space}
  ${width}
`
Divider.defaultProps = {
  my: 3,
  width: '100%'
}

Divider.displayName = 'Divider'

export default Divider
