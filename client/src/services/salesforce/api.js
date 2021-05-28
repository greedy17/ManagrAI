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

    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'fields/', {
        params: this.cls.toAPI(params),
      })

      return res.data.results.map(f => this.cls.fromAPI(f))
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }

  async getStagePicklistValues() {
    // if the picklist values dont populate for some reason allow users to manually populate
    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'picklists/refresh-stage/')
      return res
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Picklist Values' })(e)
    }
  }

  async list({ filters = {}, pagination = {} } = {}) {
    // list method that works with collection manager for pagination
    let filtersMap = {
      ...SObjectFormBuilderAPI.FILTERS_MAP,
      createable: ApiFilter.create({ key: 'createable' }),
      updateable: ApiFilter.create({ key: 'updateable' }),
      salesforceObject: ApiFilter.create({ key: 'salesforce_object' }),
      search: ApiFilter.create({ key: 'search' }),
      forAlerts: ApiFilter.create({ key: 'for_alerts' }),
      filterable: ApiFilter.create({ key: 'filterable' }),
    }

    const url = SObjectFormBuilderAPI.ENDPOINT + 'fields/'

    const options = {
      params: ApiFilter.buildParams(filtersMap, {
        ...filters,
        page: pagination.page,
        pageSize: pagination.size,
      }),
    }

    return this.client
      .get(url, options)
      .then(response => response.data)
      .then(data => ({
        ...data,
        results: data.results.map(this.cls.fromAPI),
      }))
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

export class SObjectValidationAPI extends ModelAPI {
  static ENDPOINT = 'salesforce/'
  get client() {
    return apiClient()
  }
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }

  async list({ filters = {}, pagination = {} } = {}) {
    // list method that works with collection manager for pagination
    let filtersMap = {
      ...SObjectValidationAPI.FILTERS_MAP,

      salesforceObject: ApiFilter.create({ key: 'salesforce_object' }),
    }

    const options = {
      params: ApiFilter.buildParams(filtersMap, {
        ...filters,
        page: pagination.page,
        pageSize: pagination.size,
      }),
    }

    try {
      const res = await this.client.get(SObjectFormBuilderAPI.ENDPOINT + 'validations/', options)
      return { ...res.data, results: res.data.results.map(f => this.cls.fromAPI(f)) }
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Listing Validations' })(e)
    }
  }
}
