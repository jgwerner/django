import React from 'react'
import { shallow, mount } from 'enzyme'
import { Provider } from 'react-redux'
import LoginForm, { renderField } from '../Form'
import { store } from 'utils/store'

const wrapper = mount(
  <Provider store={store}>
    <LoginForm />
  </Provider>
)

describe('Login form', () => {
  it('renders without crashing', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('should render input', () => {
    expect(wrapper.exists()).toBe(true)
    const input = wrapper.find('input').first()
    expect(input.exists()).toBe(true)
    expect(input.props().name).toEqual('username')
    input.simulate('change', { target: { value: 'user' } })
    expect((input.instance() as any).value).toBe('user')
  })

  it('handles submit', () => {
    const button = wrapper.find('button').first()
    expect(button.exists()).toBe(true)
    expect(button.props().type).toEqual('submit')
    button.simulate('click')
  })

  describe('renderTextInput', () => {
    let subject
    it('renders an error message for the input', () => {
      const input = { name: 'username', value: '' }
      const label = 'Username'
      const type = 'text'
      const meta = { touched: true, error: 'Required' }
      const element = renderField({ ...input, label, type, meta })
      subject = shallow(element)
      const usernameBlock = subject.first()
      expect(usernameBlock.exists()).toBe(true)
      expect(subject.exists()).toBe(true)
    })
  })
})