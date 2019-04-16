import React from 'react'
import Link from 'components/atoms/Link'
import Container from 'components/atoms/Container'
import styled from 'styled-components/macro'
import theme from 'utils/theme'

const Slash = styled.span`
  display: inline-block;
  margin: 0 0.6rem;
  cursor: default;
  font-size: 20px;
`

const Breadcrumbs = ({ userName, projectName }) => {
  return (
    <Container mb={theme.contentPadding}>
      <Link to={`/${userName}`} fontSize={4}>
        {userName}
      </Link>
      <Slash>/</Slash>
      <Link to={`/${userName}/${projectName}`} fontSize={5} fontWeight={500}>
        {projectName}
      </Link>
    </Container>
  )
}

export default Breadcrumbs
