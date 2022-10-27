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
            crmObject: ApiFilter.create({ key: 'crmObject' }),

            search: ApiFilter.create({ key: 'search' }),
        }

        let params = ApiFilter.buildParams(filterMaps, { ...query_params })
        try {
            const res = await this.client.get(ObjectFieldAPI.ENDPOINT + 'fields/', {
                params: this.cls.toAPI(params),
            })
            console.log(res)
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
            search: ApiFilter.create({ key: 'search' }),
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
}