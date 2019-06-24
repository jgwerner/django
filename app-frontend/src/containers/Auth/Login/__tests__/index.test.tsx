import React from 'react'
import Login from '../'
import { shallow, mount } from 'enzyme'
import { Provider } from 'react-redux'
import { store } from 'utils/store'
import { BrowserRouter as Router } from 'react-router-dom'
import LoginForm from '../'

const mockLoginfn = jest.fn()

const wrapper = mount(
  <Provider store={store}>
    <Router>
      <Login />
    </Router>
  </Provider>
)

describe('login page component', () => {
  it('renders without crashing', () => {
    shallow(<Login />)
  })

  it('renders the login form', () => {
    const form = wrapper.find('form').first()
    expect(form.exists()).toBe(true)
    beforeEach(() => {
      form.find('form').simulate('submit', { preventDefault() {} })
    })
    const usernameIput = form.find('input').first()
    expect(usernameIput.exists()).toBe(true)
    expect(usernameIput.props().name).toEqual('username')
    const button = form.find('button').first()
    expect(button.props().type).toEqual('submit')
    expect(button.exists()).toBe(true)
    // button.simulate('click')
    // expect(mockLoginfn.mock.calls.length).toEqual(1)
  })
})
