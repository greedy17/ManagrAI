import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const OPTIONS_URL = '/notifications/options/'
const SELECTIONS_URL = '/notifications/selections/'
const SETTINGS_ENDPOINT = '/notifications/settings/'
const UPDATE_SETTINGS_ENDPOINT = '/notifications/settings/update-settings/'

export class NotificationSettingsAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new NotificationSettingsAPI(cls)
  }
  async list({ pagination, filters }) {
    const url = SETTINGS_ENDPOINT
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(url, options)

      let results = {
        ...res.data,
        results: res.data.results.map(item => this.cls.fromAPI(item, 'option')),
      }

      return results
    } catch {
      apiErrorHandler({ apiName: 'Notification.Settings' })
    }
  }
  async updateSettings(options) {
    const url = UPDATE_SETTINGS_ENDPOINT
    try {
      await this.client.patch(url, options)
    } catch {
      apiErrorHandler({ apiName: 'Notification.Settings Update' })
    }
  }
}
