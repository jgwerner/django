import styled from 'styled-components/macro'
import { space, width, SpaceProps, WidthProps } from 'styled-system'

export interface ImageProps extends SpaceProps, WidthProps {}

const Image = styled.img<ImageProps>(
  {
    display: 'block',
    maxWidth: '100%',
    height: 'auto'
  },
  space,
  width
)

Image.displayName = 'Image'

Image.defaultProps = {
  m: 'auto'
}

export default Image
