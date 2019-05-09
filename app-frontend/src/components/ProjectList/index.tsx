import React from 'react'
import styled from 'styled-components/macro'
import Card from 'components/Card'
import theme from 'utils/theme'

export const Projects = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-gap: 30px;
  margin: auto;
`

const ProjectStyles = styled(Card)`
  display: flex;
  width: 100%;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  border: 1px solid ${theme.colors.gray2};
`

export const Project = (props: any) => (
  <ProjectStyles type="contentPartial" pt={4} {...props} />
)
