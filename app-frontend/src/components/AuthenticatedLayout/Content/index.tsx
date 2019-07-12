import React from 'react'
import styled from 'styled-components/macro'
import Container, { ContainerProps } from 'components/atoms/Container'
import Flex, { FlexProps } from 'components/atoms/Flex'
import theme from 'utils/theme'

interface ContentProps {
  children?: JSX.Element | JSX.Element[] | string
}

type PanelProps = FlexProps & ContentProps

export const ContentWrapper = styled(Container)<ContainerProps>`
  position: relative;
  top: 50px;
`
export const ContentPanel = styled(Flex)<PanelProps>`
  padding-top: ${theme.contentPadding};
  padding-bottom: ${theme.contentPadding};
  border: 1px solid ${theme.colors.gray2};
  position: relative;
`
export const ContentTop = styled(Flex)`
  margin: -${theme.contentPadding};
  margin-bottom: 20px;
  padding: 10px ${theme.contentPadding} 0;
  border-bottom: 1px solid ${theme.colors.gray2};
  position: static;
  z-index: 1;
  align-items: center;
  justify-content: center;
`

export const ContentTopAction = styled(Container)`
  margin-left: auto;
  padding-bottom: 10px;
`

const Content = (props: ContentProps) => (
  <ContentWrapper width={['98%', '75%']}>
    <ContentPanel
      bg="white"
      px={['25px', '50px']}
      mt="50px"
      mx="auto"
      mb="30px"
      width={1}
      {...props}
    />
  </ContentWrapper>
)

ContentTop.displayName = 'ContentTop'

export default Content
