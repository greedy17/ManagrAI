import { apiClient, apiErrorHandler } from '@/services/api'

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

  create(representative, dateRange) {
    // representative can be a repID or the constant 'ALL'
    let data = {
      representative,
      dateRange,
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
}
