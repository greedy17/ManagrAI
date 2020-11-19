import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

const TEST_CHANNEL_ENDPOINT = '/slack/test-channel/'
const TEST_DM_ENDPOINT = '/slack/test-dm/'

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
}
