import styled from 'styled-components'
import {
  space,
  width,
  borderRadius,
  SpaceProps,
  WidthProps,
  BorderRadiusProps
} from 'styled-system'
import { darken } from 'polished'
import theme from 'utils/theme'

interface ButtonProps extends SpaceProps, WidthProps, BorderRadiusProps {
  variation?: string
  size?: string
  fontSize?: string
  height?: string
  minWidth?: string
  color?: string
  backgroundColor?: string
  borderColor?: string
  cursor?: string
  opacity?: string
  outline?: string
}

const size = (props: ButtonProps) => {
  switch (props.size) {
    case 'small':
      return {
        fontSize: '12px',
        height: '30px'
      }
    case 'standard':
      return {
        fontSize: '14px',
        height: '36px',
        minWidth: '100px'
      }
    case 'large':
      return {
        fontSize: '18px',
        height: '46px',
        minWidth: '125px'
      }
    case 'icon':
      return {
        fontSize: '12px',
        height: '30px',
        maxWidth: 'fit-content'
      }
    default:
      return {}
  }
}

const variation = (props: ButtonProps) => {
  switch (props.variation) {
    case 'primary':
      return {
        color: 'white',
        backgroundColor: theme.colors.primary,
        '&:hover:not(:disabled)': {
          backgroundColor: darken(0.05, `${theme.colors.primary}`)
        },
        '&:active:not(:disabled)': {
          backgroundColor: darken(0.1, `${theme.colors.primary}`)
        }
      }
    case 'outlined':
      return {
        color: `${theme.colors.primary}`,
        backgroundColor: 'white',
        borderColor: `${theme.colors.primary}`,
        '&:hover:not(:disabled)': {
          backgroundColor: darken(0.05, `white`)
        }
      }
    case 'danger':
      return {
        color: 'white',
        backgroundColor: `${theme.colors.danger}`,
        '&:hover:not(:disabled)': {
          backgroundColor: darken(0.05, `${theme.colors.danger}`)
        },
        '&:active:not(:disabled)': {
          backgroundColor: darken(0.1, `${theme.colors.danger}`)
        }
      }
    case 'icon': {
      return {
        background: 'none',
        border: 'none',
        verticalAlign: 'middle',
        color: 'inherit'
      }
    }
    default:
      return {}
  }
}

const Button = styled.button<ButtonProps>`
  {
    cursor: pointer;
    &:disabled {
      cursor: default;
      opacity: 0.35;
    }
    outline: none;
  }
  ${space}
  ${width}
  ${size}
  ${variation}
  ${borderRadius}
`

Button.displayName = 'Button'

Button.defaultProps = {
  borderRadius: '4px',
  variation: 'primary',
  size: 'standard'
}

export default Button
