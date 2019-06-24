import React from 'react'
import { AddProjectForm } from '../Form'
import { shallow } from 'enzyme'

let mock = jest.fn()

function shallowSetup() {
  const props = {
    newProjectError: true,
    handleSubmit: mock
  }

  const wrapper: any = shallow(<AddProjectForm {...props} />)

  return {
    wrapper
  }
}

describe('add project form', () => {
  it('renders without crashing', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders form', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
    wrapper.update()
    const form = wrapper.find('Form')
    expect(form.exists()).toBe(true)
    form.simulate('submit')
    expect(mock).toHaveBeenCalledTimes(1)
  })

  it('renders the error banner only when there is an error', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
    let banner = wrapper.find('Banner')
    expect(banner.exists()).toBe(true)
    expect(banner.props().message).toEqual('Error creating new project')
    wrapper.setProps({ newProjectError: false })
    banner = wrapper.find('Banner')
    expect(banner.exists()).toBe(false)
  })
})
