import React from 'react'
import * as Sentry from '@sentry/browser'
// import ErrorImage from '../images/404-image.png'
// import Image from 'components/atoms/Image'
import Text from 'components/atoms/Text'
import Container from 'components/atoms/Container'

interface ErrorBoundaryProps {
  error: boolean
}

export default class ErrorBoundary extends React.Component<{}, { error: any }> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { error: null }
  }

  componentDidCatch(error: any, errorInfo: any) {
    this.setState({ error })
    Sentry.withScope((scope: any) => {
      Object.keys(errorInfo).forEach(key => {
        scope.setExtra(key, errorInfo[key])
      })
      Sentry.captureException(error)
    })
  }

  render() {
    if (this.state.error) {
      return (
        <Container m="auto">
          {/* <Image src={ErrorImage} /> */}
          <Text>Error</Text>
        </Container>
      )
    }
    return this.props.children
  }
}
