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
  static ENDPOINT = 'salesforce/'
  get client() {
    return apiClient()
  }
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }

  async listFields(query_params = {}) {
    let filterMaps = {
      ...SObjectFormBuilderAPI.FILTERS_MAP,
      createable: ApiFilter.create({ key: 'createable' }),
      updateable: ApiFilter.create({ key: 'updateable' }),
      salesforceObject: ApiFilter.create({ key: 'salesforceObject' }),
      search: ApiFilter.create({ key: 'search' }),
    }

    let params = ApiFilter.buildParams(filterMaps, { ...query_params })

    console.log(query_params)

    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'fields/', {
        params: this.cls.toAPI(params),
      })

      return res.data.results.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async listValidations(query_params = {}) {
    let filterMaps = {
      ...SObjectFormBuilderAPI.FILTERS_MAP,

      salesforceObject: ApiFilter.create({ key: 'salesforceObject' }),
    }

    let params = ApiFilter.buildParams(filterMaps, { ...query_params })

    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'validations/', {
        params: this.cls.toAPI(params),
      })
      return res.data.results.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
  async listPicklists(query_params = {}) {
    let filterMaps = {
      ...SObjectFormBuilderAPI.FILTERS_MAP,

      salesforceObject: ApiFilter.create({ key: 'salesforceObject' }),
      picklistFor: ApiFilter.create({ key: 'picklistFor' }),
    }

    let params = ApiFilter.buildParams(filterMaps, { ...query_params })

    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'picklists/', {
        params: this.cls.toAPI(params),
      })
      return res.data.results.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
}
