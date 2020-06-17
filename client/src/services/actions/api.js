import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const ACTIONS_ENDPOINT = '/actions/'

export default class ActionAPI {
  /**
   * Instantiate a new `ActionAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `ActionAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new ActionAPI(cls)
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
      .get(ACTIONS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'ActionAPI.list error',
        }),
      )
    return promise
  }

  create(type, detail, leads) {
    let data = {
      action: {
        action_type: type,
        action_detail: detail,
      },
      leads,
    }
    const promise = apiClient()
      .post(ACTIONS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'ActionAPI.create' }))
    return promise
  }
}
