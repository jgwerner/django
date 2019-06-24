import React from 'react'
import { Home, AsyncProjectList } from '../index'
import { shallow } from 'enzyme'

function shallowSetup() {
  let mock: any = jest.fn()

  const props = {
    profileInfoFetched: false,
    getUserInfo: mock,
    match: mock,
    history: mock,
    location: mock
  }
  const wrapper = shallow(<Home {...props} />)

  return {
    props,
    wrapper
  }
}

describe('home page component', () => {
  it('renders without crashing', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the project nav bar when profile info has been fetched', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('TabbedNav').exists()).toBe(false)
    expect(wrapper.contains(<AsyncProjectList />)).toBe(false)
    wrapper.setProps({ profileInfoFetched: true })
    wrapper.update()
    expect(wrapper.find('TabbedNav').exists()).toBe(true)
    expect(wrapper.contains(<AsyncProjectList />)).toBe(true)
    wrapper.setProps({ profileInfoFetched: false })
  })
})
