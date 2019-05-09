import axios from 'axios'
import { getToken } from 'utils/auth'

class ProjectListAPI {
  getProjectList = (username: string) => {
    const URL = `${process.env.REACT_APP_API_URL}v1/${username}/projects/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .get(URL, { headers })
      .then(response => response.data)
      .catch(error => {
        throw error
      })
  }
}

export default new ProjectListAPI()
