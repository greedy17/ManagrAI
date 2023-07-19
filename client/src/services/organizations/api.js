import { apiClient, apiErrorHandler, ApiFilter, ModelAPI } from '@/services/api'

const ORGANIZATIONS_ENDPOINT = '/organizations/'
const TEAM_ENDPOINT = '/organization/teams/'
const CHANGE_ADMIN = '/organizations/change-admin/'
const ORGANIZATIONS_UPDATE = '/organizations/update-org-info/'
const ORGANIZATIONS_DEACTIVATE = '/organizations/deactivate/'
const ADMIN_ORGS = '/organizations/admin/'

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
  async orgDeactivate(data) {
    try {
      const res = await this.client.get(ORGANIZATIONS_DEACTIVATE, { params: { org_id: data } })
      return res.data
    } catch(e) {
      console.log('error in orgDeactivate', e)
      apiErrorHandler({ apiName: 'Organization.orgDeactivate' })
    }
  }
  async changeAdmin(data) {
    return this.client
      .post(CHANGE_ADMIN, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.changeAdmin' }))
  }
  async getStaffOrganizations(org_id) {
    try {
      const response = await this.client.get(ADMIN_ORGS, { params: { org_id } })
      return response.data
    } catch(e) {
      apiErrorHandler({ apiName: 'Organization.getStaffOrganizations' })
    }
  }
  async listTeams(id) {
    try {
      const res = await this.client.get(TEAM_ENDPOINT, { params: { user: id } })
      return res.data
    } catch {
      apiErrorHandler({ apiName: 'Organization.listTeams' })
    }
  }
  async createNewTeam(data) {
    return this.client
      .post(TEAM_ENDPOINT, data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.createNewTeam' }))
  }
  async addTeamMember(data) {
    return this.client
      .post(TEAM_ENDPOINT + 'modify-membership/', data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.addTeamMember' }))
  }
  async changeTeamLead(data) {
    return this.client
      .patch(TEAM_ENDPOINT + data.id + '/', data)
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'Organization.changeTeamLead' }))
  }
}
