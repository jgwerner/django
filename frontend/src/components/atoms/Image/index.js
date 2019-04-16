import styled from 'styled-components/macro'
import { space } from 'styled-system'

const Image = styled.img(
  {
    display: 'block',
    maxWidth: '100%',
    height: 'auto'
  },
  space
)

Image.displayName = 'Image'

Image.defaultProps = {
  m: 'auto'
}

export default Image
