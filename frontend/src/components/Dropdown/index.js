import styled from 'styled-components/macro'
import { color } from 'styled-system'
import theme from 'utils/theme'

const Dropdown = styled.div`
  display: ${props => (props.show ? 'inline' : 'none')};
  position: absolute;
  z-index: 3;
  right: 0;
  width: 150px;
  margin-top: 10px;
  border: 1px solid ${theme.colors.gray2};
  ${color}
`
const ListItem = styled.li`
  list-style-type: none;
  padding: 15px;
  color: black;
  border-bottom: 1px solid ${theme.colors.gray2};
  &:hover {
    cursor: pointer;
    background-color: ${theme.colors.primary};
    color: white;
  }
`

Dropdown.displayName = 'Dropdown'

Dropdown.Item = ListItem

Dropdown.defaultProps = {
  bg: 'white'
}

export default Dropdown
