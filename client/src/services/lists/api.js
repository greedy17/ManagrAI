import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const LISTS_ENDPOINT = '/lists/'

export default class ListAPI {
  /**
   * Instantiate a new `ListAPI`
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
    return new ListAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
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
}
