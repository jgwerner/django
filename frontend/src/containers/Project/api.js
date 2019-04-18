import axios from 'axios'
import { getToken } from 'utils/auth'

class ProjectAPI {
  getProject = (username, projectName) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/?name=${projectName}`
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

export default new ProjectAPI()