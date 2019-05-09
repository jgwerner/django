import styled from 'styled-components/macro'
import {
  color,
  fontSize,
  fontWeight,
  ColorProps,
  FontSizeProps,
  FontWeightProps
} from 'styled-system'
import { Link as rrLink } from 'react-router-dom'

interface LinkProps extends ColorProps, FontSizeProps, FontWeightProps {}

const Link = styled(rrLink)<LinkProps>(
  {
    textDecoration: 'none'
  },
  color,
  fontSize,
  fontWeight
)

Link.displayName = 'Link'

Link.defaultProps = {
  color: 'link'
}

export default Link
