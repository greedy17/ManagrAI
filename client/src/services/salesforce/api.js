import { ModelAPI, ApiFilter, Model } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'

export default class SalesforceAPI extends ModelAPI {
  static ENDPOINT = 'users/salesforce/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async getAuthLink() {
    try {
      const res = await this.client.get(SalesforceAPI.ENDPOINT + 'authorization')
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async authenticate(code) {
    try {
      const res = await this.client.post(SalesforceAPI.ENDPOINT + 'authenticate', { code: code })
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async revoke() {
    try {
      const res = await this.client.post(SalesforceAPI.ENDPOINT + 'revoke')
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
}

export class SObjectFormBuilderAPI extends ModelAPI {
  async listFields() {
    try {
      const res = await this.client.get(SalesforceAPI.ENDPOINT + 'fields')
      return res.data.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async listValidations() {
    try {
      const res = await this.client.get(SalesforceAPI.ENDPOINT + 'fields')
      return res.data.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
}
