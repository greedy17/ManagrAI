import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const FORECASTS_ENDPOINT = '/forecasts/'
const GENERATE_FORECAST_ENDPOINT = uid => `/forecasts/${uid}/`

export default class ForecastAPI {
  /**
   * Instantiate a new `ForecastAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `ForecastAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new ForecastAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),

      byUser: ApiFilter.create({ key: 'by_user' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(FORECASTS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'ForecastAPI.list',
        }),
      )
    return promise
  }

  create(lead, forecast) {
    let data = { lead, forecast }
    const promise = apiClient()
      .post(FORECASTS_ENDPOINT, data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'ForecastAPI.create' }))
    return promise
  }

  update(id, data) {
    const promise = apiClient()
      .patch(GENERATE_FORECAST_ENDPOINT(id), data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'ForecastAPI.update' }))
    return promise
  }
}
