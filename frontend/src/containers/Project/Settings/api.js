import axios from 'axios'
import { getToken } from 'utils/auth'

class UpdateProjectAPI {
  updateDetails = (username, projectID, values) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      name: values.name,
      description: values.description
    }
    return axios
      .patch(URL, body, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  changeVisibility = (username, projectName, visibility) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectName}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      private: visibility
    }
    return axios
      .patch(URL, body, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  deleteProject = (username, projectName) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectName}/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .delete(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  getSearchResults = (username, value) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/search/?q=${value}&type=users&limit=5`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .get(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }
}

export default new UpdateProjectAPI()
