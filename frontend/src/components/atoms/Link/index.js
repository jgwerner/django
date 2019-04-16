import styled from 'styled-components/macro'
import { color, fontSize, fontWeight } from 'styled-system'
import { Link as rrLink } from 'react-router-dom'

const Link = styled(rrLink)(
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
