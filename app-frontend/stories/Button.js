import React from 'react'
import { storiesOf } from '@storybook/react'
import Button from '../src/components/atoms/button'

const Primary = () => (
  <div>
    <Button>Primary</Button>
    <Button disabled>Primary</Button>
  </div>
)

const Outlined = () => (
  <div>
    <Button type="outlined">Outlined</Button>
  </div>
)

storiesOf('Button', module)
  .add('Primary', () => <Primary />)
  .add('Outlined', () => <Outlined />)
