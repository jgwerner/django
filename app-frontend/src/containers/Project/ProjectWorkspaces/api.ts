import axios from 'axios'
import { getToken } from 'utils/auth'

class WorkspacesAPI {
  getServerSizes = () => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/servers/options/server-size/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .get(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  getWorkspaces = (username: string, projectID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/servers/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .get(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  startServer = (username: string, projectID: string, workspaceID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/servers/${workspaceID}/start/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .post(URL, '', { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  stopServer = (username: string, projectID: string, workspaceID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/servers/${workspaceID}/stop/`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .post(URL, '', { headers })
      .then(response => response.data)
      .catch(error => error)
  }

  deleteServer = (username: string, projectID: string, workspaceID: string) => {
    const URL = `${
      process.env.REACT_APP_API_URL
    }v1/${username}/projects/${projectID}/servers/${workspaceID}`
    const headers = {
      Accept: 'application/json',
      Authorization: getToken()
    }
    return axios
      .delete(URL, { headers })
      .then(response => response.data)
      .catch(error => error)
  }
}

export default new WorkspacesAPI()
