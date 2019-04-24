import React from 'react'
import styled from 'styled-components'
import { NavLink } from 'react-router-dom'
import theme from 'utils/theme'

export const TabbedNavGroup = styled.div`
  display: flex;
  margin-right: auto;
`
export const TabbedNavLink = styled(NavLink).attrs({
  activeClassName: 'active'
})`
  padding: 1rem 0;
  font-weight: 600;
  color: ${theme.colors.gray7};
  border-bottom: 2px solid transparent;
  text-decoration: none;
  position: relative;
  z-index: 0;
  & + & {
    margin-left: 50px;
  }
  &.active {
    color: ${theme.colors.tertiary};
    border-bottom-color: ${theme.colors.secondary};
  }
`

export const TabbedNav = props => <TabbedNavGroup {...props} />
