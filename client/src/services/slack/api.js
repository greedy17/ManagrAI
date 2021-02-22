import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import User from '@/services/users'

const TEST_CHANNEL_ENDPOINT = '/slack/test-channel/'
const TEST_DM_ENDPOINT = '/slack/test-dm/'
const GET_OAUTH_LINK_ENDPOINT = '/slack/get-oauth-link/'
const GENERATE_ACCESS_TOKEN_ENDPOINT = '/slack/generate-access-token/'
const SLACK_REVOKE_ENDPOINT = '/slack/revoke/'
const SLACK_CUSTOM_FORM_ENDPOINT = '/slack/forms/'

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
    const promise = this.client
      .post(GET_OAUTH_LINK_ENDPOINT, objectToSnakeCase(payload))
      .then(r => objectToCamelCase(r.data))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.getOAuthLink' }))
    return promise
  }

  generateAccessToken = code => {
    const payload = { code, redirectUri: this.cls.redirectURI }
    const promise = this.client
      .post(GENERATE_ACCESS_TOKEN_ENDPOINT, objectToSnakeCase(payload))
      .then(r => new User(objectToCamelCase(r.data)))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.generateAccessToken' }))
    return promise
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
  getOrgCustomForm(resource = null) {
    return this.client
      .get(SLACK_CUSTOM_FORM_ENDPOINT, { params: { resource } })
      .then(response => response.data.results.map(res => objectToCamelCase(res)))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.postOrgCustomForm', enable400Alert: false }))
  }

  postOrgCustomForm(data) {
    return this.client
      .patch(SLACK_CUSTOM_FORM_ENDPOINT + data.id + '/', data)
      .then(response => objectToCamelCase(response.data))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.postOrgCustomForm' }))
  }
}
