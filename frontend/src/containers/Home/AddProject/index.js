import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { bindActionCreators } from 'redux'
import { getFormValues } from 'redux-form'
import Modal from 'components/Modal'
import AddProjectForm from './Form'
import * as AddProjectActions from './actions'

const AddProject = props => {
  const { username, values, addProject } = props
  return (
    <React.Fragment>
      <Modal
        header="Add new project"
        body={<AddProjectForm onSubmit={() => addProject(username, values)} />}
      />
    </React.Fragment>
  )
}

const mapStateToProps = state => ({
  values: getFormValues('addProject')(state)
})

const mapDispatchToProps = dispatch =>
  bindActionCreators(
    {
      ...AddProjectActions
    },
    dispatch
  )

AddProject.propTypes = {
  username: PropTypes.string.isRequired,
  values: PropTypes.objectOf(PropTypes.array).isRequired,
  addProject: PropTypes.func.isRequired
}

export default withRouter(
  connect(
    mapStateToProps,
    mapDispatchToProps
  )(AddProject)
)
