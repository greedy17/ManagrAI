import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'
import { objectToCamelCase } from '@/services/utils'
import store from '@/store'

// API Endpoints
const LOGIN_ENDPOINT = '/login/'
const LOGIN_SSO_ENDPOINT = '/login-sso/'
const LOGOUT_ENDPOINT = '/logout/'
const REGISTRATION_ENDPOINT = '/register/'
const NOTE_TEMPLATE_ENDPOINT = '/note-template/'
const USERS_ENDPOINT = '/users/'
const USERS_UPDATE = '/users/update-user-info/'
const REVOKE_TOKEN_ENDPOINT = '/users/revoke-token/'
const REFRESH_TOKEN_ENDPOINT = '/users/refresh-token/'
const GET_USER_ENDPOINT = uid => `/users/${uid}/`
const GET_USER_PHOTO_ENDPOINT = uid => `/users/${uid}/profile-photo/`
const INVITE_ENDPOINT = '/users/invite/'
const UNINVITE_ENDPOINT = '/users/remove-user/'
const ALL_USERS_ENDPOINT = '/users/admin-users/'
const TASKS_ENDPOINT = '/users/admin-tasks/'
// const STAFF_ORGANIZATIONS = '/users/staff/organziations/'
const STAFF_WORKFLOWS = '/users/staff/meetingworkflows/'
const STAFF_FORMS = '/users/staff/slack-forms/'
const STAFF_SOBJECTS = '/users/staff/sobjectfields/'
const GENERATE_ACTIVATE_ENDPOINT = uid => `/users/${uid}/activate/`
const CHECK_STATUS_ENDPOINT = '/account-status/'
const CHECK_TASKS_ENDPOINT = '/task-status/'
const SSO_DATA_ENDPOINT = '/sso-data/'
const NYLAS_AUTH_EMAIL_LINK = '/users/email-auth-link/'
const NYLAS_SEND_EMAIL = '/users/nylas/send-new-email/'
const NYLAS_REPLY_EMAIL = '/users/nylas/reply-to-email/'
const CREATE_MESSAGING_ACCOUNT_ENDPOINT = '/users/create-twilio-account/'
const DELETE_MESSAGE_ACCOUNT_URI = '/users/remove-twilio-account/'
const PASSWORD_RESET_EMAIL_ENDPOINT = `${USERS_ENDPOINT}password/reset/link/`
const PASSWORD_RESET_ENDPOINT = `${USERS_ENDPOINT}password/reset/`
const FORECAST_ENDPOINT = '/users/modify-forecast/'
const PULL_USAGE_DATA = '/users/pull-usage-data/'
const PERFORMANCE_REPORT_ENDPOINT = '/users/performance-report/'
const TRIAL_USERS_ENDPOINT = '/users/get-trial-users/'
const FORECAST_VALUES_ENDPOINT = '/users/get-forecast-values/'
const CHAT_SUBMISSION = 'users/chat/submission/'
const CHAT_ASK = 'users/chat/ask-managr/'
const CHAT_DEAL_REVIEW = 'users/chat/deal-review/'
const CHAT_EMAIL = 'users/chat/follow-up-email/'
const CHAT_NEXT_STEPS = 'users/chat/next-steps/'
const CHAT_SUMMARY = 'users/chat/summary/'
const CHAT_MEETING = 'users/chat/submit-chat-meeting/'
const CHAT_TRANSCRIPT = 'users/chat/chat-transcript/'
const ADD_MESSAGE = 'users/chat/add-message/'
const EDIT_MESSAGE = 'users/chat/edit-message/'
const DELETE_MESSAGES = 'users/chat/delete-messages/'
const CONVERSATIONS = 'users/conversations/'

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

  async getConversations(user_id) {
    try {
      const response = await this.client.get(CONVERSATIONS, { params: user_id })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getAllOrgUsers' })
    }
  }
  async addMessage(data) {
    try {
      const res = await this.client.post(ADD_MESSAGE, data)
      return res.data
    } catch (e) {
      console.log('Error adding message: ', e)
      apiErrorHandler({ apiName: 'User.addMessage' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }
  async editMessage(data) {
    try {
      const res = await this.client.post(EDIT_MESSAGE, data)
      return res.data
    } catch (e) {
      console.log('Error editing message: ', e)
      apiErrorHandler({ apiName: 'User.editMessage' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }
  async deleteMessages() {
    try {
      const res = await this.client.post(DELETE_MESSAGES)
      return res.data
    } catch (e) {
      console.log('Error deleting message: ', e)
      apiErrorHandler({ apiName: 'User.deleteMessage' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }
  async chatUpdate(data) {
    try {
      const res = await this.client.post(CHAT_SUBMISSION, data)
      return res.data
    } catch (e) {
      console.log('Error in chatUpdate: ', e)
      apiErrorHandler({ apiName: 'User.chatUpdate' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }

  async askManagr(data) {
    try {
      const res = await this.client.post(CHAT_ASK, data)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'User.askManagr' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }

  async dealReview(data) {
    try {
      const res = await this.client.post(CHAT_DEAL_REVIEW, data)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'User.dealReview' })
      return { value: e.response.data.value, status: e.response.status }
    }
  }

  async chatEmail(data) {
    return this.client
      .post(CHAT_EMAIL, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'User.chatEmail' }))
  }

  async chatNextSteps(data) {
    return this.client
      .post(CHAT_NEXT_STEPS, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'User.chatNextSteps' }))
  }

  async getSummary(data) {
    return this.client
      .post(CHAT_SUMMARY, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'User.chatSummary' }))
  }

  async submitChatMeeting(data) {
    return this.client
      .post(CHAT_MEETING, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'User.chatMeeting' }))
  }

  async submitChatTranscript(data) {
    try {
      const response = await this.client.post(CHAT_TRANSCRIPT, data)
      console.log('response', response)
      return response.data
    } catch (e) {
      console.log('error in submitChatTranscript', e)
      apiErrorHandler({ apiName: 'User.chatMeeting' })
    }
  }

  async list({ pagination, filters }) {
    const url = USERS_ENDPOINT
    const filtersMap = {
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      active: ApiFilter.create({ key: 'active' }),
      ordering: ApiFilter.create({ key: 'ordering' }),
      search: ApiFilter.create({ key: 'search' }),
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
      console.dir(e)
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
  loginSSO(d) {
    const data = { ...d }
    const promise = apiClient()
      .post(LOGIN_SSO_ENDPOINT, data)
      .catch(
        apiErrorHandler({ apiName: 'UserAPI.ssoLogin', enable400Alert: false, enable500Alert: false }),
      )
    return promise
  }

  logout(d) {
    // const data = { ...d }
    const promise = apiClient()
      .post(LOGOUT_ENDPOINT)
      .catch(
        apiErrorHandler({ apiName: 'UserAPI.login', enable400Alert: false, enable500Alert: false }),
      )
    return promise
  }

  /* Perform logout by clearing the Vuex store. */
  // logout() {
  //   store.commit('LOGOUT_USER')
  // }

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

  uninvite(id) {
    const data = { remove_id: id }
    const promise = apiClient()
      .post(UNINVITE_ENDPOINT, this.cls.toAPI(data))
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.uninvite',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }

  async getAllOrgUsers(org_id) {
    try {
      const response = await this.client.get(ALL_USERS_ENDPOINT, { params: { org_id } })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getAllOrgUsers' })
    }
  }

  async getTasks() {
    try {
      const response = await this.client.get(TASKS_ENDPOINT)
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getTasks' })
    }
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
  async sendNewEmail(data) {
    const url = NYLAS_SEND_EMAIL
    try {
      const res = await this.client.post(url, data)
      return res
    } catch (e) {
      console.log('Error in sendNewEmail: ', e)
    }
  }
  async sendReplyEmail(data) {
    const url = NYLAS_REPLY_EMAIL
    try {
      const res = await this.client.post(url, data)
      return res
    } catch (e) {
      console.log('Error in sendNewEmail: ', e)
    }
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

  refreshCalendarEvents() {
    const promise = apiClient()
      .get(USERS_ENDPOINT + 'refresh-calendar-events/')
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

  async getUser(userId) {
    const url = GET_USER_ENDPOINT(userId)
    try {
      const response = await this.client.get(url)
      return this.cls.fromAPI(response.data)
    } catch (e) {
      console.log(e)
      apiErrorHandler({ apiName: 'Get User Profile Data API error' })
    }
  }

  getUserByEmail(email) {
    const url = USERS_ENDPOINT
    return this.client
      .get(url, { params: { email } })
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'Get User by Email API error' }))
  }
  // getUser(userId) {
  //   const url = GET_USER_ENDPOINT(userId)
  //   return this.client
  //     .get(url)
  //     .then(response => this.cls.fromAPI(response.data))
  //     .catch(apiErrorHandler({ apiName: 'Get User Profile Data API error' }))
  // }

  getForecastValues() {
    const url = FORECAST_VALUES_ENDPOINT
    return this.client
      .get(url)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Get Forecast values error' }))
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

  async revokeToken(token, userId) {
    const url = REVOKE_TOKEN_ENDPOINT
    const data = {
      token,
      user_id: userId
    }
    try {
      await this.client.post(url, data)
    } catch (e) {
      apiErrorHandler({ apiName: 'UserAPI.revokeToken' })
    }
  }
  async refreshToken(token, userId) {
    const url = REFRESH_TOKEN_ENDPOINT
    const data = {
      token,
      user_id: userId,
    }
    try {
      await this.client.post(url, data)
    } catch (e) {
      apiErrorHandler({ apiName: 'UserAPI.revokeToken' })
    }
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
  async modifyForecast(action, ids) {
    const url = FORECAST_ENDPOINT
    const data = {
      action: action,
      ids: ids
    }
    try {
      await this.client.post(url, data)
    } catch {
      apiErrorHandler({ apiName: 'API error' })
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

  async callCommand(keyword) {
    const url = `${USERS_ENDPOINT}staff/commands/`
    const data = {
      command: keyword
    }
    try {
      let res = await this.client.post(url, data)
      return res.data
    } catch (e) {
      console.log(e)
    }
  }
  pullUsageData() {
    const promise = apiClient()
      .get(PULL_USAGE_DATA)
      .catch(
        apiErrorHandler({
          apiName: 'UserAPI.activate',
          enable400Alert: false,
          enable500Alert: false,
        }),
      )
    return promise
  }
  async usersUpdate(data) {
    return this.client
      .post(USERS_UPDATE, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'User.usersUpdate' }))
  }

  createTemplate(data) {
    return this.client
      .post(NOTE_TEMPLATE_ENDPOINT, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }

  getTemplates() {
    return this.client
      .get(NOTE_TEMPLATE_ENDPOINT)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }

  removeTemplate(data) {
    return this.client
      .delete(NOTE_TEMPLATE_ENDPOINT + data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }

  updateTemplate(id, data) {
    return this.client
      .patch(NOTE_TEMPLATE_ENDPOINT + id + '/', data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }

  async checkTasks(verbose_name) {
    const url = CHECK_TASKS_ENDPOINT

    try {
      const res = await this.client.get(url, { params: { verbose_name } })
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Get Tasks error' })
    }
  }
  async googleInit() {
    const url = SSO_DATA_ENDPOINT
    try {
      const res = await this.client.get(url)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'googleInit error' })
    }
  }

  async getStaffOrganizations(org_id) {
    try {
      const response = await this.client.get(STAFF_ORGANIZATIONS, { params: { org_id } })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getStaffOrganizations' })
    }
  }
  async getStaffWorkflows(org_id) {
    try {
      const response = await this.client.get(STAFF_WORKFLOWS, { params: { org_id } })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getStaffWorkflows' })
    }
  }
  async getStaffForms(org_id) {
    try {
      const response = await this.client.get(STAFF_FORMS, { params: { org_id } })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getStaffForms' })
    }
  }
  async getStaffSObjects(org_id) {
    try {
      const response = await this.client.get(STAFF_SOBJECTS, { params: { org_id } })
      return response.data
    } catch (e) {
      apiErrorHandler({ apiName: 'UsersAPI.getStaffSObjects' })
    }
  }

  getPerformanceReport(user_id) {
    return this.client
      .get(PERFORMANCE_REPORT_ENDPOINT, { params: { user_id } })
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }
  getTrialUsers() {
    return this.client
      .get(TRIAL_USERS_ENDPOINT)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'API error' }))
  }
}
