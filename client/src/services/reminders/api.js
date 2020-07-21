import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const REMINDERS_ENDPOINT = '/reminders/'
export default class ReminderAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new ReminderAPI(cls)
  }
  async list({ pagination, filters }) {
    const url = REMINDERS_ENDPOINT
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      byLead: ApiFilter.create({ key: 'by_lead' }),
      byRemindOn: ApiFilter.create({ key: 'by_remind_on' }),
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
      apiErrorHandler({ apiName: 'ReminderAPI.list' })
    }
  }
  async create(noteDetails) {
    // notes are created with {note:{title:'',content:''}, leads:[]}
    let data = { ...noteDetails }
    data = this.cls.toAPI(data)
    const url = REMINDERS_ENDPOINT
    try {
      const res = await this.client.post(url, data)
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'ReminderAPI.create' })
    }
  }
  async delete(noteId) {
    const url = REMINDERS_ENDPOINT
    try {
      await this.client.delete(url + noteId)
    } catch (e) {
      apiErrorHandler({ apiName: 'ReminderAPI.delete' })
    }
  }
}
