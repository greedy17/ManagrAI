import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'

export default class ZoomAPI extends ModelAPI {
  static ENDPOINT = 'users/zoom/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new ZoomAPI(cls)
  }
  async getAuthLink() {
    try {
      const res = await this.client.get(ZoomAPI.ENDPOINT + 'authorization')
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async getAuthData(code) {
    try {
      const res = await this.client.post(ZoomAPI.ENDPOINT + 'authenticate', { code: code })
      return res
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }

  async revokeAccess() {
    try {
      await this.client.delete(ZoomAPI.ENDPOINT + 'revoke')
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }
  /**
   * Endpoint to create instant zoom meeting this is available for Dev and Staging only
   */
  async createMeeting() {
    try {
      const res = await this.client.post('zoom/api/meetings')
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Creating Meeting' })(e)
    }
  }
}
