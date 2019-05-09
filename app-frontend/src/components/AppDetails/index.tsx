import styled from 'styled-components'
import Container, { ContainerProps } from '../atoms/Container'
import Button from '../atoms/Button'

interface ExpandProps extends ContainerProps {
  show: boolean
}

export const Expand = styled(Container)<ExpandProps>`
  display: ${props => (props.show ? 'block' : 'none')};
`

export const Details = styled(Container)`
  word-break: break-word;
`
export const ToggleButton = styled(Container)`
  &:hover {
    cursor: pointer;
  }
`

export const DeleteButtonWrapper = styled(Container)`
  max-width: fit-content;
  float: right;
  position: relative;
`

export const DeleteButton = styled(Button)`
  max-width: fit-content;
  min-width: fit-content;
  &:hover {
    cursor: pointer;
  }
`

export const ToolTip = styled(Container)`
  ${DeleteButtonWrapper}:hover & {
    display: block;
  }
  display: none;
  width: max-content;
  position: absolute;
  font-size: 12px;
  top: -35px;
  padding: 8px;
  background: rgb(0, 0, 0, 0.65);
  border-radius: 2px;
  color: white;
`
