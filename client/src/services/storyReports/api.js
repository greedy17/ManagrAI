import { apiClient, apiErrorHandler } from '@/services/api'

// API Endpoints
const STORY_REPORTS_ENDPOINT = '/story-reports/'
const GENERATE_STORY_REPORT_ENDPOINT = id => STORY_REPORTS_ENDPOINT + id + '/'
export default class StoryReportAPI {
  /**
   * Instantiate a new `StoryReportAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `StoryReportAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new StoryReportAPI(cls)
  }

  create(lead) {
    // is the lead ID
    let data = {
      lead,
    }
    const promise = apiClient()
      .post(STORY_REPORTS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'StoryReportAPI.create' }))
      .then(response => this.cls.fromAPI(response.data))
    return promise
  }

  retrieve(id) {
    const promise = apiClient()
      .get(GENERATE_STORY_REPORT_ENDPOINT(id))
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'StoryReportAPI.retrieve' }))
    return promise
  }
}
