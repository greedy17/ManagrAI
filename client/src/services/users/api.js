import { API_BASE, apiClient, apiErrorHandler } from '@/services/api'
import store from '@/store'

// API Endpoints
const LOGIN_ENDPOINT = `${API_BASE}login/`
const INVITE_ENDPOINT = `${API_BASE}users/invite/`
const GENERATE_ACTIVATE_ENDPOINT = uid => `${API_BASE}users/${uid}/activate/`

export default class UserAPI {
  /**
   * Instantiate a new `UserAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `UserAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new UserAPI(cls)
  }

  login(email, password) {
    const data = { email, password }
    const promise = apiClient()
      .post(LOGIN_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'UserAPI.login' }))
    return promise
  }

  /* Perform logout by clearing the Vuex store. */
  logout() {
    store.commit('LOGOUT_USER')
  }

  invite(email, type, organization) {
    const data = { email, type, organization }
    const promise = apiClient()
      .post(INVITE_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'UserAPI.invite' }))
    return promise
  }

  activate(uid, token, password) {
    const data = { token, password }
    const promise = apiClient()
      .post(GENERATE_ACTIVATE_ENDPOINT(uid), data)
      .catch(apiErrorHandler({ apiName: 'UserAPI.activate' }))
    return promise
  }
}
