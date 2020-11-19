import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

const TEST_MESSAGE_ENDPOINT = '/slack-test-message/'

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

  sendTestMessage(data) {
    const promise = this.client
      .post(TEST_MESSAGE_ENDPOINT, objectToSnakeCase(data))
      .then(r => objectToCamelCase(r.data))
      .catch(apiErrorHandler({ apiName: 'SlackAPI.sendTestMessage' }))
    return promise
  }
}
