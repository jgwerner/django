import React from 'react'
import styled from 'styled-components/macro'
import { space, textAlign, SpaceProps, TextAlignProps } from 'styled-system'
import Text from 'components/atoms/Text'
import Container from 'components/atoms/Container'
import Icon from 'components/Icon'
import theme from 'utils/theme'
import Heading from 'components/atoms/Heading'
import history from 'utils/history'

interface ModalProps extends SpaceProps, TextAlignProps {
  children?: JSX.Element | JSX.Element[] | string
  onClick?: () => void
  header?: string
  body?: JSX.Element | JSX.Element[] | string
}

export const ModalHeader = styled.div<ModalProps>`
  border: 1px solid ${theme.colors.borderMedium};
  box-sizing: border-box;
  border-radius: 4.8px 4.8px 0px 0px;
  height: 64px;
  background-color: white;
  ${space}
  ${textAlign}
`
const ModalTitle = styled(Heading)`
  position: relative;
  top: 50%;
  transform: translateY(-50%);
`

const ModalBody = styled.div`
  border: 1px solid ${theme.colors.borderMedium};
  border-top: none;
  border-bottom: none;
  box-sizing: border-box;
  min-height: 64px;
  background-color: white;
  ${space}
  ${textAlign}
`

const BG = styled.div`
  display: block;
  position: fixed;
  background-color: rgba(0, 0, 0, 0.4);
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  z-index: 10;
`
const ModalContainer = styled(Container)`
  position: fixed;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  overflow: auto;
  height: auto;
  min-height: 250px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  z-index: 15;
`

const CloseButton = styled(Icon)`
  position: absolute;
  top: 10px;
  right: 10px;
  &:hover {
    cursor: pointer;
  }
`
export const Overlay = (props: ModalProps) => <BG {...props} />

export const ModalCard = (props: ModalProps) => (
  <ModalContainer mx="auto" bg="white" width={1 / 3} {...props} />
)

export const ModalContent = (props: any) => (
  <Text fontWeight={600} p={4} {...props} />
)

export default class Modal extends React.PureComponent<ModalProps> {
  handleClick = () => history.goBack()

  render() {
    const { handleClick, props } = this
    return (
      <React.Fragment>
        <Overlay onClick={handleClick} />
        <ModalCard {...props}>
          <ModalHeader {...props} p={3}>
            <ModalTitle size="h3" my="0">
              {props.header}
            </ModalTitle>
            <CloseButton size="25" type="close" onClick={handleClick} />
          </ModalHeader>
          <ModalBody textAlign="center" p={3} {...props}>
            {props.body}
          </ModalBody>
        </ModalCard>
      </React.Fragment>
    )
  }
}
