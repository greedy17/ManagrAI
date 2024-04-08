import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToSnakeCase } from '@/services/utils'
import store from '../../store'

class CommsApi extends ModelAPI {
    static ENDPOINT = 'prsearch/'

    static FILTERS_MAP = {
        page: ApiFilter.create({ key: 'page' }),
        pageSize: ApiFilter.create({ key: 'page_size' }),
    }

    get client() {
        // store.dispatch('updateAbortController', new AbortController())
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

    async deletePitch(data) {
        try {
            const res = await this.client.delete(`pitches/${data.id}/`,)
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

    async regeneratePitch(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'regenerate-pitch/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async generatePitch(data) {
        try {
            const res = await this.client.post('pitches/generate/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async regeneratePitch(data) {
        try {
            const res = await this.client.post('pitches/regenerate/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async savePitch(data) {
        try {
            const res = await this.client.post('pitches/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getJournalists(data) {
        try {
            const res = await this.client.post('pitches/journalists/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getFeedback(data) {
        try {
            const res = await this.client.post('pitches/feedback/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async regenerateWithFeedback(data) {
        try {
            const res = await this.client.post('pitches/regenerate-feedback/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async regenerateTranscript(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'regenerate-pitch/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async generateTranscript(data) {
        try {
            const res = { data: { transcript: 'transcript' } }
            // const res = await this.client.post(CommsApi.ENDPOINT + 'pitch/', data)
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
    async getPitches() {
        try {
            const res = await this.client.get('pitches/')
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
    async getClips(data, signal) {
        try {
            const res = await this.client.get('pr/clips/', { signal, params: data })
            console.log(res)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getSummary(data, signal) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'summary/', data, { signal })
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

    async regenerateArticleSummary(url, summary, instructions) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'regenerate-article-summary/', { params: url, summary, instructions })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async generateContent(url, instructions, style) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'generate-content/', { params: url, instructions, style })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getWebSummary(url, instructions) {
        console.log('here')
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'web-summary/', { params: url, instructions })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async uploadLink(url) {
        try {
            const res = await this.client.post('users/comms/upload-link/', { params: url })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getWritingStyles(data) {
        try {
            const res = await this.client.get('writing-styles/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async saveWritingStyle(data) {
        try {
            const res = await this.client.post('pitches/learn/', { params: data })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async deleteWritingStyle(data) {
        try {
            const res = await this.client.post('pitches/delete-style/', { params: data })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getAllEmailAlerts() {
        try {
            const res = await this.client.get('email-alerts/get-email-alerts/')
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getEmailAlerts() {
        try {
            const res = await this.client.get('email-alerts/')
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async addEmailAlert(data) {
        try {
            const res = await this.client.post('email-alerts/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async testEmailAlert(data) {
        try {
            const res = await this.client.post('email-alerts/test-alert/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async removeEmailAlert(data) {
        try {
            const res = await this.client.delete(`email-alerts/${data.id}/`)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async sendSummaryEmail(data) {
        try {
            const res = await this.client.post(CommsApi.ENDPOINT + 'email-summary/', data)
            return res
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }

    async getDetails() {
        try {
            const res = await this.client.get('details/')
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async addDetails(data) {
        try {
            const res = await this.client.post('details/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async removeDetails(data) {
        try {
            const res = await this.client.delete(`details/${data.id}/`)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async getProcesses() {
        try {
            const res = await this.client.get('process/')
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async createProcess(data) {
        try {
            const res = await this.client.post('process/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async runProcess(data) {
        try {
            const res = await this.client.post('process/run/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async deleteProcess(data) {
        try {
            const res = await this.client.delete(`process/${data.id}/`)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async summarizePDF(data) {
        try {
            const res = await this.client.post('summarize-pdf/', data, { headers: { "Content-Type": "multipart/form-data" } })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
    async discoverJournalists(data) {
        try {
            const res = await this.client.post('discover/', data)
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
        }
    }
}

class TwitterAccountAPI extends ModelAPI {
    static ENDPOINT = 'users/twitter/'
    static FILTERS_MAP = {
        page: ApiFilter.create({ key: 'page' }),
        pageSize: ApiFilter.create({ key: 'page_size' }),
    }
    get client() {
        // store.dispatch('updateAbortController', new AbortController())
        return apiClient(store.state.abortController)
    }
    static create(cls) {
        return new TwitterAccountAPI(cls)
    }
    async getAuthLink() {
        try {
            const res = await this.client.get(TwitterAccountAPI.ENDPOINT + 'authorization')
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Salesloft Auth Link' })(e)
        }
    }
    async authenticate(code, verifier) {
        try {
            const res = await this.client.post(TwitterAccountAPI.ENDPOINT + 'authenticate', { code: code, verifier: verifier })
            return res.data
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
        }
    }
    async revoke() {
        try {
            await this.client.delete(TwitterAccountAPI.ENDPOINT + 'revoke')
        } catch (e) {
            apiErrorHandler({ apiName: 'Error Retrieving Data from Code' })(e)
        }
    }
}

export { CommsApi, TwitterAccountAPI }