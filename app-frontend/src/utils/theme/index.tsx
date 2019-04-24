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
  borderMedium: '#D6DFE5'
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