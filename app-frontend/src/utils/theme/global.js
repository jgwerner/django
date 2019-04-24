import { createGlobalStyle } from 'styled-components'
import theme from '.'

const Global = createGlobalStyle`
* {
  box-sizing: border-box;
}
*:before,
*:after {
  box-sizing: border-box;
}
  body {
    padding: 0;
    margin: 0;
    font-family: Roboto, sans-serif;
    background-color: ${theme.colors.backdrop};
  }
`

export default Global
