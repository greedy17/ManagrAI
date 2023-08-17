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

    async deleteSearch(data) {
        try {
            const res = await this.client.delete(CommsApi.ENDPOINT + `${data.id}/`,)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async upateSearch(data) {
        try {
            const res = await this.client.patch(CommsApi.ENDPOINT + 'update/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async createSearch(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT, data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async generatePitch(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'pitch/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getSearches() {
        try {
            const res = await this.client.get(CommsApi.ENDPOINT)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getTweets(data) {
        try {
            const res = await this.client.get(CommsApi.ENDPOINT + 'tweets/', { params: data })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
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
            const res = await this.client.post(CommsApi.ENDPOINT + 'summary/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getTweetSummary(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'tweet-summary/', data)
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