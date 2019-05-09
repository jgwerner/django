import 'styled-components'

declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      primary: string
      secondary: string
      white: string
      tertiary: string
      success: string
      info: string
      warning: string
      danger: string
      gray1: string
      gray2: string
      gray3: string
      gray4: string
      gray5: string
      gray6: string
      gray7: string
      gray8: string
      gray9: string
      backdrop: string
      link: string
      blueLight: string
      textLight: string
      borderMedium: string
      textError: string

      infoText: string
      infoIcon: string
      unfoButton: string
      infoAlertBorder: string
      infoAlertBackground: string

      successText: string
      successButton: string
      successIcon: string
      successAlertBorder: string
      successAlertBackground: string
      successBadge: string

      dangerButton: string
      dangerIcon: string
      dangerAlertBorder: string
      dangerAlertBackground: string

      warningText: string
      warningAlertBorder: string
      WarningAlertBackground: string
      warningIcon: string
    }
    space: number[]
    fontSizes: number[]
    contentPadding: string
  }
}
