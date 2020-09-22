import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const PERFORMANCE_REPORTS_ENDPOINT = '/performance-reports/'
const GENERATE_PERFORMANCE_REPORT_ENDPOINT = id => PERFORMANCE_REPORTS_ENDPOINT + id + '/'

export default class PerformanceReportAPI {
  /**
   * Instantiate a new `PerformanceReportAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `PerformanceReportAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new PerformanceReportAPI(cls)
  }

  get client() {
    return apiClient()
  }

  create(representative, dateRangePreset, dateRanges) {
    // representative can be a repID or the constant 'ALL'
    let data = {
      representative,
      dateRangePreset,
      ...dateRanges,
    }
    const promise = apiClient()
      .post(PERFORMANCE_REPORTS_ENDPOINT, this.cls.toAPI(data))
      .catch(apiErrorHandler({ apiName: 'PerformanceReportAPI.create' }))
      .then(response => this.cls.fromAPI(response.data))
    return promise
  }

  retrieve(id) {
    const promise = apiClient()
      .get(GENERATE_PERFORMANCE_REPORT_ENDPOINT(id))
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'PerformanceReportAPI.retrieve' }))
    return promise
  }

  async list({ pagination, filters }) {
    const url = PERFORMANCE_REPORTS_ENDPOINT
    const filtersMap = {
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
    } catch (e) {
      apiErrorHandler({ apiName: 'PerformanceReportAPI.list' })
    }
  }
}
