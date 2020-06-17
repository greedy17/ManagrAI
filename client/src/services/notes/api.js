import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const NOTES_ENDPOINT = '/notes/'
const NOTES_BULK_ENDPOINT = '/notes/bulk/'

export default class NoteAPI {
  constructor(cls) {
    this.cls = cls
  }

  get client() {
    return apiClient()
  }

  static create(cls) {
    return new NoteAPI(cls)
  }

  async list({ pagination, filters }) {
    const url = NOTES_ENDPOINT
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

  async create(note) {
    const url = NOTES_ENDPOINT
    const data = this.cls.toAPI(note)

    try {
      const res = await this.client.post(url, data)
      return this.cls.fromAPI(res.data)
    } catch (error) {
      apiErrorHandler({ apiName: 'NotesAPI.create' })(error)
    }
  }

  /**
   * Bulk create notes
   *
   * Notes can be created in bulk with this payload:
   *
   *    {
   *       note: {
   *         title: '',
   *         content: ''
   *       },
   *       created_for: []
   *    }
   */
  async bulkCreate(noteDetails) {
    let data = { ...noteDetails }

    const promise = apiClient()
      .post(NOTES_BULK_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NoteAPI.bulkCreate' }))
    return promise
  }
}
