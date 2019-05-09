import React from 'react'
import LogoIcon from 'images/logo-mark.svg'
import Image, { ImageProps } from '../atoms/Image'

const Logo: React.FunctionComponent<ImageProps> = () => (
  <Image width="45px" mt="0" src={LogoIcon} />
)

export default Logo
