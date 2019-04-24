import React from 'react'
import styled from 'styled-components/macro'
import Container from 'components/atoms/Container'
import Flex from 'components/atoms/Flex'
import theme from 'utils/theme'

export const ContentWrapper = styled(Container)`
  position: relative;
  width: 75%;
  top: 50px;
`
export const ContentPanel = styled(Flex)`
  padding: ${theme.contentPadding};
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

const Content = props => (
  <ContentWrapper>
    <ContentPanel
      bg="white"
      mt="50px"
      mx="auto"
      mb="30px"
      width={1}
      {...props}
    />
  </ContentWrapper>
)

export default Content
