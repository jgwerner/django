import { DefaultTheme } from 'styled-components'

const colors = {
  primary: '#5c7f00',
  secondary: '#f47920',
  tertiary: '#182540',
  success: '#28d1bd',
  info: '#b6bbd1',
  warning: '#f49f20',
  danger: '#ff4747',
  white: '#fff',
  gray1: '#f0f1f2',
  gray2: '#e7e9eb',
  gray3: '#d0d3d8',
  gray4: '#b9bdc5',
  gray5: '#a2a7b2',
  gray6: '#8b929f',
  gray7: '#747c8c',
  gray8: '#5d6679',
  gray9: '#465066',
  gray10: '#2f3a53',
  backdrop: '#f8f9fc',
  link: '#5c7f00',
  blueLight: '#fafbff',
  textLight: '#acb2bf',
  borderMedium: '#D6DFE5',

  textError: '#E12D39',

  infoText: '#105789',
  infoIcon: '#3E8DC0',
  unfoButton: '#59A2D0',
  infoAlertBorder: '#73B4DA',
  infoAlertBackground: '#C9E1EE',

  successText: '#0E7326',
  successButton: '#1D923B',
  successIcon: '#2DA74C',
  successAlertBorder: '#68DB8B',
  successAlertBackground: '#A5F3BE',
  successBadge: '#D0F9DE',

  dangerButton: '#B1091F',
  dangerIcon: '#E12D39',
  dangerAlertBorder: '#F86B6F',
  dangerAlertBackground: '#F2D2CD',

  warningText: '#9B7527',
  warningAlertBorder: '#DABA84',
  WarningAlertBackground: '#EFE0CE',
  warningIcon: '#EFE0CE'
}

const contentPadding = '50px'

const space = [0, 4, 8, 16, 32, 64, 128]

const fontSizes = [10, 12, 14, 16, 18, 20, 24, 30, 38, 48, 64]

const theme: DefaultTheme = {
  colors,
  space,
  fontSizes,
  contentPadding
}

export default theme
