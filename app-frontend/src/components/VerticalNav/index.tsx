import React, { Fragment } from 'react'
import styled from 'styled-components/macro'
import { NavLink } from 'react-router-dom'
import theme from '../../utils/theme'
import Icon from '../../components/Icon'



export const VerticalNavLayout = styled.div`
  display: flex;
  margin-top: ${(props: {project?: boolean}) => (props.project ? theme.contentPadding : '')};
  width: 100%;
`
export const VerticalNavLayoutMenu = styled.div`
  margin: -${theme.contentPadding};
  margin-right: 0;
  padding-top: ${theme.contentPadding};
  padding-right: ${theme.contentPadding};
  background-color: ${theme.colors.blueLight};
  border-right: 1px solid ${theme.colors.gray2};
  width: 300px;
`
export const VerticalNavLayoutContent = styled.div`
  margin: 0 ${theme.contentPadding};
  width: 100%;
`
export const VerticalNavLink = styled(NavLink).attrs({
  activeClassName: 'active'
})`
  display: block;
  margin-bottom: 40px;
  padding-right: 20px;
  font-weight: 500;
  color: ${theme.colors.tertiary};
  text-align: right;
  transition: all 0.3s ease-in;
  position: relative;
  text-decoration: none;
  &:hover {
    color: ${theme.colors.primary};
  }
  &.active {
    color: ${theme.colors.primary};
  }
`
export const VerticalNavIcon = styled(Icon).attrs({
  type: 'arrowRight',
  size: 18
})`
  position: absolute;
  right: 0;
  top: 0;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.1s ease-in-out;
  transition-property: opacity, transform;
  .active > & {
    opacity: 1;
    transform: translateX(0);
  }
`
export const VerticalNavMenu = ({ links }: any) => (
  <Fragment>
    {links.map(({ children, ...props }: any) => (
      <VerticalNavLink key={props.to} {...props}>
        {children}
        <VerticalNavIcon />
      </VerticalNavLink>
    ))}
  </Fragment>
)