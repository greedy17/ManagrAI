import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const LISTS_ENDPOINT = '/lists/'
const BULK_UPDATE_ENDPOINT = '/lists/bulk-update/'

export default class ListAPI {
  /**
   * Instantiate a new `ListAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  /**
   * Factory method to create a new instance of `UserAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new ListAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      byUser: ApiFilter.create({ key: 'by_user' }),
      byLead: ApiFilter.create({ key: 'by_lead' }),
      ordering: ApiFilter.create({ key: 'ordering' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(LISTS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'ListAPI.list error',
        }),
      )
    return promise
  }

  create(title) {
    let data = { title }
    const promise = apiClient()
      .post(LISTS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'ListAPI.create' }))
    return promise
  }
  async deleteList(listId) {
    const url = `${LISTS_ENDPOINT}${listId}`
    try {
      await this.client.delete(url)
    } catch (e) {
      apiErrorHandler({ apiName: 'ListAPI.create' })
    }
  }
  async removeFromList(leads, listId) {
    // array of leads to remove
    const url = `${LISTS_ENDPOINT}${listId}/remove-from-list/`
    try {
      await this.client.post(url, { leads })
    } catch (e) {
      apiErrorHandler({ apiName: 'ListAPI.removeFromList' })
    }
  }
  async addToList(leads, listId) {
    // array of leads to add
    const url = `${LISTS_ENDPOINT}${listId}/add-to-list/`
    try {
      await this.client.post(url, { leads })
    } catch (e) {
      apiErrorHandler({ apiName: 'ListAPI.removeFromList' })
    }
  }

  bulkUpdate(leads, lists) {
    // all leads in request params to be processed to only be in the lists present in request params
    let data = { leads, lists }
    const promise = apiClient()
      .post(BULK_UPDATE_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'ListAPI.bulkUpdate' }))
    return promise
  }
}
