import React from 'react'
import styled from 'styled-components/macro'
import Container, { ContainerProps } from 'components/atoms/Container'
import Flex, { FlexProps } from 'components/atoms/Flex'
import theme from 'utils/theme'

const HeaderWrapper = styled(Container)<ContainerProps>`
  position: fixed;
  z-index: 1;
  height: 60px;
  box-shadow: 0 1px 3px ${theme.colors.gray1};
`

const HeaderContent = styled(Flex)<FlexProps>`
  height: 100%;
`
const HeaderItems = styled(Flex)<FlexProps>`
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  width: 100%;
`

export const HeaderItemsLeft = styled(Flex)`
  padding-right: 20px;
`

export const HeaderItemsRight = styled(Flex)`
  margin-left: auto;
  align-items: center;
`
export const Item = styled(Container)`
  margin: ${theme.space[1]}px;
`
export const DropdownWrapper = styled.div`
  display: inline-block;
  position: relative;
  &:hover {
    cursor: pointer;
  }
`

const DownArrowSvg = (props: any) => (
  <svg width="8" height="6" xmlns="http://www.w3.org/2000/svg" {...props}>
    <path
      fill="currentColor"
      d="M6.959 0H.54a.3.3 0 0 0-.254.459l3.209 5.134a.3.3 0 0 0 .508 0L7.214.459A.3.3 0 0 0 6.958 0z"
    />
  </svg>
)

export const DownArrow = styled(DownArrowSvg)`
  color: ${theme.colors.gray7};
`

interface HProps {
  children: JSX.Element | JSX.Element[] | string
}

export const Header = (props: HProps) => (
  <HeaderWrapper width="100%" bg="white" {...props}>
    <HeaderContent mx="auto" my="0px" width={7.5 / 10} {...props}>
      <HeaderItems {...props} />
    </HeaderContent>
  </HeaderWrapper>
)
