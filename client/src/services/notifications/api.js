import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const NOTIFICATIONS_ENDPOINT = '/notifications/'
const UNVIEWED_COUNT_URI = 'unviewed-notifications-count/'
export default class NotificationAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new NotificationAPI(cls)
  }
  async list({ pagination, filters }) {
    const url = NOTIFICATIONS_ENDPOINT
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

      return {
        ...res.data,
        results: res.data.results.map(this.cls.fromAPI),
      }
    } catch {
      apiErrorHandler({ apiName: 'Notification.list' })
    }
  }
  async getUnviewedCount({ pagination, filters }) {
    const url = NOTIFICATIONS_ENDPOINT + UNVIEWED_COUNT_URI
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

      const results = {
        count: res.data.count,
      }

      return results
    } catch {
      apiErrorHandler({ apiName: 'Notification.list' })
    }
  }
}
