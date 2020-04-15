import { apiClient, apiErrorHandler } from '@/services/api'

// API Endpoints
const GENERATE_UNCLAIM_ENDPOINT = uid => `/leads/${uid}/un-claim/`

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

  unclaim(uid) {
    const promise = apiClient()
      .delete(GENERATE_UNCLAIM_ENDPOINT(uid))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.unclaim' }))
    return promise
  }
}
