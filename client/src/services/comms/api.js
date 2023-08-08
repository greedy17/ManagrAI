import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToSnakeCase } from '@/services/utils'

export default class CommsApi extends ModelAPI {
    static ENDPOINT = 'prsearch/'

    static FILTERS_MAP = {
        page: ApiFilter.create({ key: 'page' }),
        pageSize: ApiFilter.create({ key: 'page_size' }),
    }

    get client() {
        return apiClient()
    }

    static create(cls) {
        return new CommsApi(cls)
    }

    async getClips(data) {
        try {
            const res = await this.client.get(CommsApi.ENDPOINT + 'clips/', { params: data })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getSummary(data) {
        try {
            const res = await this.client.get(CommsApi.ENDPOINT + 'summary/', { params: data })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getArticleSummary(url, search, instructions) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'article-summary/', { params: url, search, instructions })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
}