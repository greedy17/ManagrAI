import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import User from '@/services/users'
import { SlackListResponse, SlackUserList } from '.'
import { SlackFormInstance } from './index'

const TEST_CHANNEL_ENDPOINT = '/slack/test-channel/'
const TEST_DM_ENDPOINT = '/slack/test-dm/'
const GET_OAUTH_LINK_ENDPOINT = '/slack/get-oauth-link/'
const GENERATE_ACCESS_TOKEN_ENDPOINT = '/slack/generate-access-token/'
const SLACK_REVOKE_ENDPOINT = '/slack/revoke/'
const SLACK_CUSTOM_FORM_ENDPOINT = '/slack/forms/'
const SLACK_LIST_PUBLIC_CHANNELS_ENDPOINT = '/slack/list-channels/'
const SLACK_LIST_CHANNELS_ENDPOINT = '/slack/list-user-channels/'
const SLACK_LIST_USERS = '/slack/list-users/'
const SLACK_CREATE_CHANNEL = '/slack/create-channel/'
const SLACK_LIST_INSTANCES = '/slack/instances/'
const SLACK_ZOOM_CHANNEL_UPDATE = '/slack/update-zoom-channel/'
const ZOOM_RECAP_CHANNEL_UPDATE = '/slack/update-recap-channel/'
const SLACK_CHANNEL_DETAILS = '/slack/channel-details/'
const ADMIN_FORMS = '/slack/forms/admin/'
const ADMIN_FORM_INSTANCES = '/slack/instances/admin/'

export default class SlackAPI {
  constructor(cls) {
    this.cls = cls
  }
  static create(cls) {
    return new SlackAPI(cls)
  }
  get client() {
    return apiClient()
  }

  getOAuthLink = linkType => {
    const payload = { linkType, redirectUri: this.cls.redirectURI }
    payload.redirectUri =
      process.env.NODE_ENV == 'development'
        ? process.env.VUE_APP_SLACK_FRONTEND_REDIRECT + '/api/users/slack/re-direct'
        : this.cls.redirectURI
    const promise = this.client
      .post(GET_OAUTH_LINK_ENDPOINT, objectToSnakeCase(payload))
      .then(r => objectToCamelCase(r.data))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.getOAuthLink', rethrowErrors: true }))
    return promise
  }

  generateAccessToken = code => {
    const payload = { code, redirectUri: this.cls.redirectURI }
    payload.redirectUri =
      process.env.NODE_ENV == 'development'
        ? process.env.VUE_APP_SLACK_FRONTEND_REDIRECT + '/api/users/slack/re-direct'
        : this.cls.redirectURI
    try {
      const res = this.client.post(GENERATE_ACCESS_TOKEN_ENDPOINT, objectToSnakeCase(payload))
      return new User(objectToCamelCase(res.data))
    } catch (e) {
      apiErrorHandler({ apiName: 'SlackAPI.getOAuthLink', rethrowErrors: true })
    }
  }

  testChannel = () => {
    const promise = this.client
      .get(TEST_CHANNEL_ENDPOINT)
      .catch(apiErrorHandler({ apiName: 'SlackAPI.testChannel' }))
    return promise
  }

  testDM = () => {
    const promise = this.client
      .get(TEST_DM_ENDPOINT)
      .catch(apiErrorHandler({ apiName: 'SlackAPI.testDM' }))
    return promise
  }

  async revoke() {
    try {
      await this.client.post(SLACK_REVOKE_ENDPOINT)
    } catch {
      apiErrorHandler({ apiName: 'SlackAPI.testDM' })
    }
  }

  // Org Custom Slack Forms
  getOrgCustomForm(resource = null, fromAdmin = false) {
    return this.client
      .get(SLACK_CUSTOM_FORM_ENDPOINT, { params: { resource, fromAdmin } })
      .then(response => (response.data.results.map(res => this.cls.customSlackForm.fromAPI(res))))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.getOrgCustomForm', enable400Alert: false }))
  }

  postOrgCustomForm(data) {
    console.log(data)
    if (data.id && data.id.length) {
      return this.client
        .patch(SLACK_CUSTOM_FORM_ENDPOINT + data.id + '/', this.cls.customSlackForm.toAPI(data))
        .then(response => this.cls.customSlackForm.fromAPI(response.data))
        .catch(apiErrorHandler({ apiName: 'SlackAPI.postOrgCustomForm' }))
    }
    return this.client
      .post(SLACK_CUSTOM_FORM_ENDPOINT, this.cls.customSlackForm.toAPI(data))
      .then(response => this.cls.customSlackForm.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.postOrgCustomForm' }))
  }

  delete(id) {
    return this.client
      .delete(SLACK_CUSTOM_FORM_ENDPOINT + id + '/')
      .then(response => response)
      .catch(apiErrorHandler({ apiName: 'SlackAPI.postOrgCustomForm' }))
  }
  async listChannels(cursor) {
    return this.client
      .post(SLACK_LIST_PUBLIC_CHANNELS_ENDPOINT, { cursor: cursor })
      .then(response => {
        return SlackListResponse.fromAPI(response.data)
      })
      .catch(apiErrorHandler({ apiName: 'SlackAPI.listChannels' }))
  }
  async listUserChannels(cursor) {
    return this.client
      .post(SLACK_LIST_CHANNELS_ENDPOINT, { cursor: cursor })
      .then(response => {
        return SlackListResponse.fromAPI(response.data)
      })
      .catch(apiErrorHandler({ apiName: 'SlackAPI.listUserChannels' }))
  }

  async listUsers(cursor) {
    return this.client
      .post(SLACK_LIST_USERS, { cursor: cursor })
      .then(response => {
        return SlackUserList.fromAPI(response.data)
      })
      .catch(apiErrorHandler({ apiName: 'SlackAPI.listUsers' }))
  }

  async createChannel(data) {
    return this.client
      .post(SLACK_CREATE_CHANNEL, { name: data })
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'SlackAPI.createChannel' }))
  }

  async channelDetails(channel_id) {
    return this.client
      .get(SLACK_CHANNEL_DETAILS, { params: { channel_id } })
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'SlackApi.channelDetails' }))
  }

  async slackFormInstances() {
    return this.client
      .get(SLACK_LIST_INSTANCES)
      .then(response => {
        return response.data.results.map(res => SlackFormInstance.fromAPI(res))
      })
      .catch(apiErrorHandler({ apiName: 'SlackApi.slackInstances' }))
  }

  async updateZoomChannel(slack_id, zoom_channel) {
    return this.client
      .post(SLACK_ZOOM_CHANNEL_UPDATE, { slack_id: slack_id, zoom_channel: zoom_channel })
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'SlackApi.updateZoomChannel' }))
  }

  async updateRecapChannel(slack_id, recap_channel, users) {
    return this.client
      .post(ZOOM_RECAP_CHANNEL_UPDATE, { slack_id: slack_id, recap_channel: recap_channel, users: users })
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'SlackApi.updateRecapChannel' }))
  }

  async getStaffForms(org_id) {
    try {
      const response = await this.client.get(ADMIN_FORMS, { params: { org_id } })
      return response.data
    } catch(e) {
      apiErrorHandler({ apiName: 'SlackApi.getStaffForms' })
    }
  }
  async getStaffFormInstances(org_id) {
    try {
      const response = await this.client.get(ADMIN_FORM_INSTANCES, { params: { org_id } })
      return response.data
    } catch(e) {
      apiErrorHandler({ apiName: 'SlackApi.getStaffFormInstances' })
    }
  }
}