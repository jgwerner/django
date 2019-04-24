import styled from 'styled-components'
import Container, { ContainerProps } from '../atoms/Container'

interface ExpandProps extends ContainerProps {
  show: boolean
}

export const Expand = styled(Container)<ExpandProps>`
  display: ${(props)  => (props.show ? 'block' : 'none')};
`

export const Details = styled(Container)`
  word-break: break-word;
`
export const ToggleButton = styled(Container)`
  &:hover {
    cursor: pointer;
  }
`
export const DeleteButton = styled(Container)`
  &:hover {
    cursor: pointer;
  }
`
