import styled from 'styled-components/macro'
import { space } from 'styled-system'
import theme from 'utils/theme'

const Divider = styled.hr`
  border: 0;
  border-bottom: 1px solid ${theme.colors.gray2};
  ${space}
`
Divider.defaultProps = {
  my: 3,
  width: '100%'
}

Divider.displayName = 'Divider'

export default Divider
