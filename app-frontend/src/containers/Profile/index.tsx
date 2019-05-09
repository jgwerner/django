import React from 'react'
import { withRouter, RouteComponentProps } from 'react-router-dom'
import Loadable from 'react-loadable'
import Avatar from 'react-avatar'
import Heading from '../../components/atoms/Heading'
import Flex from '../../components/atoms/Flex'
import theme from '../../utils/theme'
import { ContentTop } from '../../components/AuthenticatedLayout/Content'
import { TabbedNav, TabbedNavLink } from '../../components/TabbedNav'
import Container from '../../components/atoms/Container'

interface ProfileRouteProps {
  userName: string
  url: string
}

const AsyncProjectList = Loadable({
  loader: () => import('../Home/ProjectList'),
  loading: () => <div />
})

const Profile = (props: RouteComponentProps<ProfileRouteProps>) => {
  const { match } = props
  return (
    <Container width="100%">
      <Flex alignItems="center" mb={5}>
        <Avatar
          name={match.params.userName}
          size="125px"
          textSizeRatio={2}
          round
          color={theme.colors.gray7}
        />
        <Heading mx={4}>{match.params.userName}</Heading>
      </Flex>
      <ContentTop>
        <TabbedNav>
          <TabbedNavLink to={`${match.url}`}>Projects</TabbedNavLink>
        </TabbedNav>
      </ContentTop>
      <AsyncProjectList />
    </Container>
  )
}

export default withRouter(Profile)
