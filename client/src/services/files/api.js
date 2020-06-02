import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const FILES_ENDPOINT = '/files/'

export default class FileAPI {
  /**
   * Instantiate a new `FileAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `UserAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new FileAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      byLead: ApiFilter.create({ key: 'by_lead' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(FILES_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'FileAPI.list',
        }),
      )
    return promise
  }

  create(file, leadID) {
    let data = new FormData()
    data.append('file', file)
    // data.append('doc_type', type)
    data.append('lead', leadID)

    const promise = apiClient()
      .post(FILES_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'FileAPI.create' }))
    return promise
  }
  create(file, leadID) {
    let data = new FormData()
    data.append('file', file)
    // data.append('doc_type', type)
    data.append('lead', leadID)

    const promise = apiClient()
      .post(FILES_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'FileAPI.create' }))
    return promise
  }
}
