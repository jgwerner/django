import React from 'react'
import styled from 'styled-components'
import {
  space,
  width,
  borders,
  borderRadius,
  textAlign,
  lineHeight,
  SpaceProps,
  WidthProps,
  BorderProps,
  BorderRadiusProps,
  TextAlignProps,
  LineHeightProps
} from 'styled-system'
import Flex from '../atoms/Flex'
import Container from '../atoms/Container'
import Icon from '../Icon'
import theme from 'utils/theme'
import Button from 'components/atoms/Button'

interface BannerProps
  extends SpaceProps,
    WidthProps,
    BorderProps,
    BorderRadiusProps,
    TextAlignProps,
    LineHeightProps {
  info?: boolean
  success?: boolean
  danger?: boolean
  warning?: boolean
  message?: string
  children?: JSX.Element[] | JSX.Element | string | string[]
  action?: any
}

interface TypeProps extends BannerProps {
  backgroundColor?: string
  color?: string
  borderColor?: string
}

const info = (props: TypeProps) =>
  props.info
    ? {
        backgroundColor: `${theme.colors.infoAlertBackground}`,
        color: `${theme.colors.infoText}`,
        borderColor: `${theme.colors.infoAlertBorder}`
      }
    : null

const success = (props: TypeProps) =>
  props.success
    ? {
        backgroundColor: `${theme.colors.successAlertBackground}`,
        color: `${theme.colors.successText}`,
        borderColor: `${theme.colors.successAlertBorder}`
      }
    : null

const danger = (props: TypeProps) =>
  props.danger
    ? {
        backgroundColor: `${theme.colors.dangerAlertBackground}`,
        color: `${theme.colors.textError}`,
        borderColor: ` ${theme.colors.dangerAlertBorder}`
      }
    : null

const warning = (props: TypeProps) =>
  props.warning
    ? {
        backgroundColor: `${theme.colors.WarningAlertBackground}`,
        color: `${theme.colors.warningText}`,
        borderColor: `${theme.colors.warningAlertBorder}`
      }
    : null

const BannerWrapper = styled(Container)<BannerProps>(
  {
    height: '50px',
    display: 'block',
    position: 'relative',
    borderRadius: 4,
    border: '1px solid'
  },
  space,
  width,
  borders,
  borderRadius,
  textAlign,
  lineHeight,
  info,
  success,
  danger,
  warning
)

const Banner = (props: BannerProps) => (
  <BannerWrapper {...props}>
    <Flex width={1}>
      <Container width="95%">{props.message}</Container>
      <Container width="5%" pl={4} textAlign="end">
        <Button size="icon" variation="icon" onClick={props.action}>
          <Icon type="close" size="20px" />
        </Button>
      </Container>
    </Flex>
  </BannerWrapper>
)

Banner.displayName = 'Banner'

Banner.defaultProps = {
  borderRadius: 4,
  border: '1px solid',
  m: 'auto',
  px: 4,
  textAlign: 'justify',
  width: '910px',
  lineHeight: '50px'
}

export default Banner
