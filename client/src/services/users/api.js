import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import store from '@/store'

// API Endpoints
const LOGIN_ENDPOINT = '/login/'
const REGISTRATION_ENDPOINT = '/register/'
const USERS_ENDPOINT = '/users/'
const GET_USER_ENDPOINT = uid => `/users/${uid}/`
const GET_USER_PHOTO_ENDPOINT = uid => `/users/${uid}/profile-photo/`
const INVITE_ENDPOINT = '/users/invite/'
const GENERATE_ACTIVATE_ENDPOINT = uid => `/users/${uid}/activate/`
const CHECK_STATUS_ENDPOINT = '/account-status/'
const NYLAS_AUTH_EMAIL_LINK = '/users/email-auth-link/'
const CREATE_MESSAGING_ACCOUNT_ENDPOINT = '/users/create-twilio-account/'
const DELETE_MESSAGE_ACCOUNT_URI = '/users/remove-twilio-account/'
const PASSWORD_RESET_EMAIL_ENDPOINT = `${USERS_ENDPOINT}password/reset/link/`
const PASSWORD_RESET_ENDPOINT = `${USERS_ENDPOINT}password/reset/`

export default class UserAPI {
  get client() {
    return apiClient()
  }

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

  async list({ pagination, filters }) {
    const url = USERS_ENDPOINT
    const filtersMap = {
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      active: ApiFilter.create({ key: 'active' }),
      ordering: ApiFilter.create({ key: 'ordering' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(url, options)

      return {
        ...res.data,
        results: res.data.results.map(this.cls.fromAPI),
      }
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.list' })
    }
  }

  login(d) {
    const data = { ...d }
    const promise = apiClient()
      .post(LOGIN_ENDPOINT, data)
      .catch(
        apiErrorHandler({ apiName: 'UserAPI.login', enable400Alert: false, enable500Alert: false }),
      )
    return promise
  }

  /* Perform logout by clearing the Vuex store. */
  logout() {
    store.commit('LOGOUT_USER')
  }

  /**
   * Register a new user
   *
   * @param {UserRegistrationForm} registerForm - A form containing first name, last name, email,
   *                                              password, and organization name.
   */
  register(registerForm) {
    const data = registerForm.toAPI()

    return this.client
      .post(REGISTRATION_ENDPOINT, this.cls.toAPI(data))
      .then(response => response.data)
      .then(data => this.cls.fromAPI(data))
      .catch(
        apiErrorHandler({
          apiName: 'Register User',
          enable400Alert: true,
          enable500Alert: true,
        }),
      )
  }

  invite(userDetails) {
    const data = userDetails

    const promise = apiClient()
      .post(INVITE_ENDPOINT, this.cls.toAPI(data))
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.invite',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }

  activate(uid, token, form) {
    const formData = this.cls.toAPI(form.toAPI())
    const data = { token, ...formData }
    const promise = apiClient()
      .post(GENERATE_ACTIVATE_ENDPOINT(uid), data)
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.activate',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }
  retrieveEmail(uid, token) {
    /**
     * Checks user email from id to add to form
     */
    let q = { id: uid, token: token }
    const promise = apiClient()
      .get(USERS_ENDPOINT + 'retrieve-email/', { params: q })
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.activate',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }

  checkStatus(email) {
    const data = { email }
    const promise = apiClient()
      .post(CHECK_STATUS_ENDPOINT, data)
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.checkStatus',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }

  getUser(userId) {
    const url = GET_USER_ENDPOINT(userId)
    return this.client
      .get(url)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'Get User Profile Data API error' }))
  }

  update(id, data) {
    const promise = apiClient()
      .patch(GET_USER_ENDPOINT(id), this.cls.toAPI(data))
      .catch(apiErrorHandler({ apiName: 'UserAPI.update' }))
    return promise
  }

  updateProfilePhoto(id, file) {
    let data = new FormData()
    data.append('file', file)

    const promise = apiClient()
      .patch(GET_USER_PHOTO_ENDPOINT(id), data)
      .catch(apiErrorHandler({ apiName: 'UserAPI.updateProfilePhoto' }))
    return promise
  }

  async createMessagingAccount(phoneNumber) {
    const url = CREATE_MESSAGING_ACCOUNT_ENDPOINT
    const data = {
      phone_number: phoneNumber,
    }
    try {
      await this.client.post(url, data)
    } catch {
      apiErrorHandler({ apiName: 'UserAPI.Messaging' })
    }
  }
  async deleteMessagingAccount() {
    const url = DELETE_MESSAGE_ACCOUNT_URI
    try {
      await this.client.post(url)
    } catch {
      apiErrorHandler({ apiName: 'UserAPI.Messaging' })
    }
  }

  requestPasswordReset(email) {
    const url = PASSWORD_RESET_EMAIL_ENDPOINT
    const obj = {
      email: email,
    }

    return this.client
      .post(url, obj)
      .then(response => objectToCamelCase(response))
      .catch(
        apiErrorHandler({
          apiName: 'Request Password Reset API',
        }),
      )
  }

  resetPassword(newPassword, uid, token) {
    const url = PASSWORD_RESET_ENDPOINT
    const data = {
      password: newPassword,
      user_id: uid,
      token,
    }
    return this.client
      .post(url, data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }
}
