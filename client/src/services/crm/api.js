import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToSnakeCase } from '@/services/utils'

export class ObjectFieldAPI extends ModelAPI {
    static ENDPOINT = 'crm/'

    static FILTERS_MAP = {
        page: ApiFilter.create({ key: 'page' }),
        pageSize: ApiFilter.create({ key: 'page_size' }),
    }
    get client() {
        return apiClient()
    }

    async listFields(query_params = {}) {
        let filterMaps = {
            ...ObjectFieldAPI.FILTERS_MAP,
            createable: ApiFilter.create({ key: 'createable' }),
            updateable: ApiFilter.create({ key: 'updateable' }),
            crmObject: ApiFilter.create({ key: 'crm_object' }),

            search: ApiFilter.create({ key: 'search' }),
        }

        let params = ApiFilter.buildParams(filterMaps, { ...query_params })
        try {
            const res = await this.client.get(ObjectFieldAPI.ENDPOINT + 'fields/', {
                params: this.cls.toAPI(params),
            })
            return res.data.results.map(f => this.cls.fromAPI(f))
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
        }
    }

    async list({ filters = {}, pagination = {} } = {}) {
        // list method that works with collection manager for pagination
        let filtersMap = {
            ...ObjectFieldAPI.FILTERS_MAP,
            createable: ApiFilter.create({ key: 'createable' }),
            updateable: ApiFilter.create({ key: 'updateable' }),
            crmObject: ApiFilter.create({ key: 'crm_object' }),
            search: ApiFilter.create({ key: 'search' }),
            forAlerts: ApiFilter.create({ key: 'for_alerts' }),
            filterable: ApiFilter.create({ key: 'filterable' }),
        }

        const url = ObjectFieldAPI.ENDPOINT + 'fields/'

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

    async getObjects(crm_object, page = 1, for_filter = false, filters = false, resource_id = false,) {
      try {
        const res = await this.client.get('crm-objects/', { params: { crm_object: crm_object, page: page, resource_id: resource_id, for_filter: for_filter, filters: JSON.stringify(filters), page_size: 20, } })
        return res.data
      } catch (e) {
        apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
      }
    }

    async getCurrentValues(formData) {
      let d = objectToSnakeCase(formData)
      try {
        const res = await this.client.get(ObjectFieldAPI.ENDPOINT + 'crm-objects/get-current-values/', { params: d })
        return res.data
      } catch (e) {
        apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
      }
    }

    async updateResource(formData) {
      try {
        const res = await this.client.post(ObjectFieldAPI.ENDPOINT + 'crm-objects/update/', formData)
        console.log('res updateResource HS', res)
        return res.data
      } catch (e) {
        return apiErrorHandler({ apiName: 'Salesforce API' })(e)
      }
    }
}