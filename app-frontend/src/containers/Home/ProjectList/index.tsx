import React from 'react'
import { bindActionCreators, Dispatch } from 'redux'
import { connect } from 'react-redux'
import { distanceInWordsToNow } from 'date-fns'
import { Project, Projects } from 'components/ProjectList'
import Icon from 'components/Icon'
import Heading from 'components/atoms/Heading'
import Text from 'components/atoms/Text'
import Link from 'components/atoms/Link'
import {getProjectList} from './actions'
import { StoreState } from 'utils/store'


interface ProjectsListMapStateToProps {
  projectsFetched: boolean
  username: string,
  projects: any
}

interface ProjectsListMapDispatchToProps {
  getProjectList: (username: string) => void,
}

type ProjectsListProps = ProjectsListMapStateToProps & ProjectsListMapDispatchToProps

const ProjectList = class extends React.Component<ProjectsListProps> {
  componentDidMount() {
    const { username, getProjectList } = this.props
    getProjectList(username)
  }

  render() {
    const { projects, username, projectsFetched } = this.props
    return (
      <React.Fragment>
        {!projectsFetched ? (
          <Projects />
        ) : (
          <Projects>
            {projects.map((project: any) => (
              <Project key={project.id}>
                {project.private ? (
                  <Icon size="25" type="private" />
                ) : (
                  <Icon size="25" type="public" />
                )}
                <Text mt={2} color="gray7">
                  {project.owner}
                </Text>
                <Heading size="h4">
                  <Link to={`/${username}/${project.name}`}>
                    {project.name}
                  </Link>
                </Heading>
                <Text color="gray7">
                  {project.description || <span>&nbsp;</span>}
                </Text>
                <Text mt={4} mb={2} color="gray7">
                  Updated {distanceInWordsToNow(project.last_updated)} ago
                </Text>
              </Project>
            ))}
          </Projects>
        )}
      </React.Fragment>
    )
  }
}

const mapStateToProps = (state: StoreState) => ({
  projects: state.home.projects.projects,
  projectsFetched: state.home.projects.projectsFetched,
  username: state.home.user.username
})

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(
    {
      getProjectList
    },
    dispatch
  )

export default 
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ProjectList)

