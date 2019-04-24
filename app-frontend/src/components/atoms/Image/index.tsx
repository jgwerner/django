import styled from 'styled-components/macro'
import { space, SpaceProps } from 'styled-system'

interface ImageProps extends SpaceProps {}

const Image = styled.img<ImageProps>(
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
