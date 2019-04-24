import axios from 'axios'
import { getToken } from '../../../utils/auth'

class AddProjectAPI {
  addProject = (username: string, values: {name: string, description: string, private: string}) => {
    const URL = `${process.env.REACT_APP_API_URL}v1/${username}/projects/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      name: values.name,
      description: values.description,
      private: values.private === 'true'
    }
    return axios
      .post(URL, body, { headers })
      .then(response => response.data)
      .catch(error => error)
  }
}

export default new AddProjectAPI()
