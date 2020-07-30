import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const LEAD_MESSAGE_ENDPOINT = '/lead-message/'

export default class LeadMessageAPI {
  constructor(cls) {
    this.cls = cls
  }

  get client() {
    return apiClient()
  }
  static create(cls) {
    return new LeadMessageAPI(cls)
  }
  async list({ pagination, filters }) {
    const filtersMap = {
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(LEAD_MESSAGE_ENDPOINT, options)
      console.log(res)
      return {
        ...res,
        results: res.data.results.map(this.cls.fromAPI),
      }
    } catch {
      apiErrorHandler({
        apiName: 'LeadMessageAPI.list error',
      })
    }
  }
}
