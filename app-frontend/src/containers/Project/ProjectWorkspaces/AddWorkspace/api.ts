import axios from 'axios'
import { getToken } from 'utils/auth'

class AddWorkspaceAPI {
  addWorkspace = (
    username: string,
    serverSize: any,
    projectID: string,
    values: { name: string }
  ) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/servers/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    const body = {
      server_size: serverSize.id,
      config: {
        type: 'jupyter'
      },
      image_name: process.env.REACT_APP_JUPYTER_IMG,
      name: values.name
    }
    return axios
      .post(URL, body, { headers })
      .then(response => response.data)
      .catch(error => {
        throw error
      })
  }
}

export default new AddWorkspaceAPI()
