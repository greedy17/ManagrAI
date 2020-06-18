import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const CALL_NOTE_ENDPOINT = '/call-notes/'
export default class CallNoteAPI {
  constructor(cls) {
    this.cls = cls
  }

  get client() {
    return apiClient()
  }

  static create(cls) {
    return new CallNoteAPI(cls)
  }

  async list({ pagination, filters }) {
    const url = CALL_NOTE_ENDPOINT
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      byLead: ApiFilter.create({ key: 'by_lead' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(url, options)
      return {
        ...res.data,
        results: res.data.results.map(this.cls.fromAPI),
      }
    } catch {
      apiErrorHandler({ apiName: 'NotesAPI.list' })
    }
  }

  async create(callNote) {
    const url = CALL_NOTE_ENDPOINT
    const data = this.cls.toAPI(callNote)

    try {
      const res = await this.client.post(url, data)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'NotesAPI.create' })(e)
    }
  }
}
