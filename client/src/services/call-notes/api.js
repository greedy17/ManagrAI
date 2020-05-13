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
      byUser: ApiFilter.create({ key: 'by_lead' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(url, options)
      return res
    } catch {
      apiErrorHandler({ apiName: 'NotesAPI.list' })
    }
  }
  async create(noteDetails) {
    // notes are created with {note:{title:'',content:''}, leads:[]}
    let data = { ...noteDetails }
    data = this.cls.toAPI(data)

    const url = CALL_NOTE_ENDPOINT
    try {
      const res = await this.client.post(url, data)
      this.$Alert.alert({
        type: 'success',
        timeout: 4000,
        message: 'note created!',
      })
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'NotesAPI.create' })
    }
  }
}
