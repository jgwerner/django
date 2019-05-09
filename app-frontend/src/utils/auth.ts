const TOKEN_KEY = 'illumidesk_token'
const TOKEN_TYPE_KEY = 'illumidesk_token_type'

const getItem = (key: string) => () => window.localStorage.getItem(key)
const setItem = (key: string) => (value: string) =>
  window.localStorage.setItem(key, value)
const removeItem = (key: string) => () => window.localStorage.removeItem(key)

const getAuthToken: any = () => {
  const token = getItem(TOKEN_KEY)()
  const tokenType = getItem(TOKEN_TYPE_KEY)()
  if (!token) return
  return `${tokenType} ${token}`
}
const setAuthToken = (token: string, type: string) => {
  setItem(TOKEN_KEY)(token)
  setItem(TOKEN_TYPE_KEY)(type)
}
const removeAuthToken = () => {
  removeItem(TOKEN_KEY)()
  removeItem(TOKEN_TYPE_KEY)()
}

export function login(token: string, type: string) {
  setAuthToken(token, type)
}

export function isLoggedIn() {
  return !!getAuthToken(TOKEN_TYPE_KEY + TOKEN_KEY)
}

export function logout() {
  removeAuthToken()
}

export const getToken = () => getAuthToken(TOKEN_TYPE_KEY + TOKEN_KEY)
