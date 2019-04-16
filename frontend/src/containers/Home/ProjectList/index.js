import React from 'react'
import PropTypes from 'prop-types'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { distanceInWordsToNow } from 'date-fns'
import * as ProjectActions from 'containers/Project/actions'
import { Project, Projects } from 'components/ProjectList'
import Icon from 'components/Icon'
import Heading from 'components/atoms/Heading'
import Text from 'components/atoms/Text'
import Link from 'components/atoms/Link'
import * as ProjectListActions from './actions'

const ProjectList = class extends React.PureComponent {
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
            {projects.map(project => (
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

const mapStateToProps = state => ({
  projects: state.home.projects.projects,
  projectsFetched: state.home.projects.projectsFetched,
  isFetching: state.home.projects.isFetching,
  username: state.home.user.username
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...ProjectListActions,
      ...ProjectActions
    },
    dispatch
  )

ProjectList.propTypes = {
  username: PropTypes.string.isRequired,
  projectsFetched: PropTypes.bool.isRequired,
  getProjectList: PropTypes.func.isRequired,
  projects: PropTypes.arrayOf(PropTypes.object).isRequired
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(ProjectList)
)
