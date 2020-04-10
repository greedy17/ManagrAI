import { API_BASE, apiClient, apiErrorHandler } from '@/services/api'

// API Endpoints
const GENERATE_DELETE_ENDPOINT = uid => `${API_BASE}leads/${uid}/`

export default class LeadAPI {
  /**
   * Instantiate a new `LeadAPI`
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
    return new LeadAPI(cls)
  }

  delete(uid) {
    const promise = apiClient()
      .delete(GENERATE_DELETE_ENDPOINT(uid))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.delete' }))
    return promise
  }
}
