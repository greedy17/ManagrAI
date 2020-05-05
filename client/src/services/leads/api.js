import { apiClient, apiErrorHandler } from '@/services/api'

// API Endpoints
const LEADS_ENDPOINT = '/leads/'
const GENERATE_LEAD_ENDPOINT = uid => `/leads/${uid}/`
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

  create(title, account, contacts) {
    let data = {
      title,
      account,
      notes: [],
      lists: [],
      contacts,
    }
    const promise = apiClient()
      .post(LEADS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'LeadAPI.create' }))
    return promise
  }

  retrieve(id) {
    const promise = apiClient()
      .get(GENERATE_LEAD_ENDPOINT(id))
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.retrieve' }))
    return promise
  }

  update(id, data) {
    const promise = apiClient()
      .patch(GENERATE_LEAD_ENDPOINT(id), data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.update' }))
    return promise
  }
}
