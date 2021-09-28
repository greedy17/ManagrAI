import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import axios from 'axios'
import CSRF from '@/services/csrf'
import API_BASE from '@/services/api/base'

export default class GongAccountAPI extends ModelAPI {
  static ENDPOINT = 'users/gong/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new GongAccountAPI(cls)
  }
  async getAuthLink() {
    try {
      const res = await this.client.get(GongAccountAPI.ENDPOINT + 'authorization')
      console.log(res)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Gong Auth Link' })(e)
    }
  }
  async authenticate(code) {
    try {
      const res = await this.client.post(GongAccountAPI.ENDPOINT + 'authenticate', { code:code})
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }

  async revoke() {
    try {
      await this.client.delete(GongAccountAPI.ENDPOINT + 'revoke')
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }
}