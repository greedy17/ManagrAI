import { apiClient, apiErrorHandler, ApiFilter, ModelAPI } from '@/services/api'

const ORGANIZATIONS_ENDPOINT = '/organizations/'
const TEAM_ENDPOINT = '/organization/teams/'//modify-membership/ // <-- This is for adding members to different teams (and deleting, kind of)
const ORGANIZATIONS_UPDATE = '/organizations/update-org-info/'

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
      fromAdmin: ApiFilter.create({ key: 'fromAdmin' })
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }
    try {
      const res = await this.client.get(url, options)
      return {
        ...res.data,
        results: res.data.results.map(this.cls.fromAPI)
      }
    } catch {
      apiErrorHandler({ apiName: 'Organization.list' })
    }
  }
  async orgUpdate(data) {
    return this.client
      .post(ORGANIZATIONS_UPDATE, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.orgUpdate' }))
  }
  async createNewTeam(data) {
    return this.client
      .post(TEAM_ENDPOINT, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.createNewTeam' }))
  }
}
