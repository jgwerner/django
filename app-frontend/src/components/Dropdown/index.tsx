import styled from 'styled-components/macro'
import { color, ColorProps, fontSize, FontSizeProps } from 'styled-system'
import theme from 'utils/theme'

export interface DropdownProps extends ColorProps {
  show: boolean
}

export interface DropdownItemProps extends FontSizeProps {
  noHover?: boolean
}

const Dropdown = styled.div<DropdownProps>`
  display: ${props => (props.show ? 'inline' : 'none')};
  position: absolute;
  z-index: 3;
  right: 0;
  width: 150px;
  margin-top: 10px;
  border: 1px solid ${theme.colors.gray2};
  ${color}
`

export const DropdownSection = styled.div`
  border-bottom: 1px solid ${theme.colors.gray2};
  padding: 10px 0;
`

export const DropdownItem = styled.li<DropdownItemProps>`
  list-style-type: none;
  padding: 8px;
  color: black;
  &:hover {
    cursor: ${props => (props.noHover ? 'default' : 'pointer')};
    background-color: ${props =>
      props.noHover ? 'white' : theme.colors.primary};
    color: ${props => (props.noHover ? 'black' : 'white')};
  }
  ${fontSize}
`

Dropdown.displayName = 'Dropdown'

DropdownItem.displayName = 'DropdownItem'

Dropdown.defaultProps = {
  bg: 'white'
}

DropdownItem.defaultProps = {
  fontSize: 2
}

export default Dropdown
