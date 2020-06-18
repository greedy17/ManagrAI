import { objectToCamelCase } from '@thinknimble/tn-utils'
import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const LEAD_ACTIVITY_ENDPOINT = '/lead-activity/'
const INSIGHTS_ENDPOINT = `${LEAD_ACTIVITY_ENDPOINT}insights/`

export default class LeadActivityLogAPI {
  constructor(cls) {
    this.cls = cls
  }

  get client() {
    return apiClient()
  }

  static create(cls) {
    return new LeadActivityLogAPI(cls)
  }

  async list({ pagination, filters }) {
    const url = LEAD_ACTIVITY_ENDPOINT
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      lead: ApiFilter.create({ key: 'lead' }),
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
    } catch (error) {
      apiErrorHandler({ apiName: 'LeadActivityLogAPI.list' })(error)
    }
  }

  async create(callNote) {
    throw Error('Lead Activity Logs may not be created through the API.')
  }

  async getInsights({ filters }) {
    const url = INSIGHTS_ENDPOINT
    const filtersMap = {
      lead: ApiFilter.create({ key: 'lead' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...filters }),
    }

    try {
      const response = await this.client.get(url, options)
      return objectToCamelCase(response.data)
    } catch (error) {
      apiErrorHandler({ apiName: 'LeadActivityLogAPI.list' })(error)
    }
  }
}
