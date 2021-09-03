import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import axios from 'axios'
import CSRF from '@/services/csrf'
import API_BASE from '@/services/api/base'

export default class SalesloftAccountAPI extends ModelAPI {
  static ENDPOINT = 'users/salesloft/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new SalesloftAccountAPI(cls)
  }
  async getAuthLink() {
    try {
      const res = await this.client.get(SalesloftAccountAPI.ENDPOINT + 'authorization')
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Salesloft Auth Link' })(e)
    }
  }
  async authenticate(code, context, scope) {
    try {
      const res = await this.client.post(SalesloftAccountAPI.ENDPOINT + 'authenticate', { code: code, context: context, scope:scope})
      return res
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }

  async revoke() {
    try {
      await this.client.delete(SalesloftAccountAPI.ENDPOINT + 'revoke')
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
    }
  }
}