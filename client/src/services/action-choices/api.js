import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const ACTION_CHOICES_ENDPOINT = '/action-choices/'

export default class ActionChoiceAPI {
  /**
   * Instantiate a new `ActionChoiceAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `ActionChoiceAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new ActionChoiceAPI(cls)
  }

  get client() {
    return apiClient()
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
      .get(ACTION_CHOICES_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'ActionChoiceAPI.list error',
        }),
      )
    return promise
  }

  create(obj, fields = [], excludeFields = []) {
    const url = ACTION_CHOICES_ENDPOINT
    const data = this.cls.toAPI(obj, fields, excludeFields)
    const options = {}

    return this.client
      .post(url, data, options)
      .then(response => response.data)
      .then(data => this.cls.fromAPI(data))
  }
  delete(id) {
    const url = ACTION_CHOICES_ENDPOINT + id
    const options = {}
    console.log(id)

    return this.client
      .delete(url, options)
      .then(response => response.data)
      .then(data => this.cls.fromAPI(data))
  }
}
