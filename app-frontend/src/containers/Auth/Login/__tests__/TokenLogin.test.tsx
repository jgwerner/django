import React from 'react'
import { shallow } from 'enzyme'
import TokenLogin from '../'

describe('Token login page', () => {
  it('renders without crashing', () => {
    shallow(<TokenLogin />)
  })
})
