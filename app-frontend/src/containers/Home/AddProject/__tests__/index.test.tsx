import React from 'react'
import AddProject from '../index'
import { mount } from 'enzyme'
import { store } from 'utils/store'
import { Provider } from 'react-redux'
import addProject from '../reducer'

function shallowSetup() {
  let mock: any = jest.fn()

  const props = {
    username: 'username',
    values: {},
    addProject: mock
  }
  const wrapper = mount(
    <Provider store={store}>
      <AddProject {...props} />
    </Provider>
  )

  return {
    props,
    wrapper
  }
}

describe('add project component', () => {
  it('renders without crashing', () => {
    const { wrapper } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the add project modal', () => {
    const { wrapper, props } = shallowSetup()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('Connect(AddProject)').exists()).toBe(true)
    const modalWrapper = wrapper.find('Modal')
    expect(modalWrapper.exists()).toBe(true)
    expect(modalWrapper.props().header).toEqual('Add new project')
    const form = modalWrapper.find('AddProjectForm')
    // console.log('form', form.props())
    expect(form.exists()).toBe(true)
    // form.simulate('submit', addProject )
    // expect(props.addProject).toHaveBeenCalledTimes(1)
  })
})
