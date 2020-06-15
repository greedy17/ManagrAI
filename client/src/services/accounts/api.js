import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const ACCOUNTS_ENDPOINT = '/accounts/'

export default class AccountAPI {
  /**
   * Instantiate a new `AccountAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `AccountAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new AccountAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      ordering: ApiFilter.create({ key: 'ordering' }),
    }

    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(ACCOUNTS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'AccountAPI.list error',
        }),
      )
    return promise
  }

  create({ name, url, type }) {
    let data = {
      name,
      url,
      type,
    }
    const promise = apiClient()
      .post(ACCOUNTS_ENDPOINT, data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(
        apiErrorHandler({
          apiName: 'AccountAPI.create error',
        }),
      )
    return promise
  }
}
