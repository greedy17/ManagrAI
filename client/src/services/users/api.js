import { API_BASE, apiClient, apiErrorHandler } from '@/services/api'
import store from '@/store'

// API Endpoints
const LOGIN = `${API_BASE}login/`

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

  static login(email, password) {
    const data = { email, password }
    const promise = apiClient()
      .post(LOGIN, data)
      .catch(apiErrorHandler({ apiName: 'UserAPI.login' }))
    return promise
  }

  /* Perform logout by clearing the Vuex store. */
  logout() {
    store.commit('LOGOUT_USER')
  }
}
