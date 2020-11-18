import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const ORGANIZATIONS_ENDPOINT = '/organizations/'
const GENERATE_SLACK_INTEGRATION_ENDPOINT = uid => `/organizations/${uid}/integrate-slack/`

export default class OrganizationAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new OrganizationAPI(cls)
  }
  async list({ pagination, filters }) {
    const url = ORGANIZATIONS_ENDPOINT
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
      apiErrorHandler({ apiName: 'Organization.list' })
    }
  }

  integrateSlack(uid, data) {
    const promise = this.client
      .post(GENERATE_SLACK_INTEGRATION_ENDPOINT(uid), this.cls.toAPI(data))
      .then(r => this.cls.fromAPI(r.data))
      .catch(apiErrorHandler({ apiName: 'OrganizationAPI.integrateSlack' }))
    return promise
  }
}
