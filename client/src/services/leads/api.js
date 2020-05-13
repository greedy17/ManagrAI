import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const LEADS_ENDPOINT = '/leads/'
const GENERATE_LEAD_ENDPOINT = uid => `/leads/${uid}/`
const GENERATE_CLAIM_ENDPOINT = uid => `/leads/${uid}/claim/`
const GENERATE_UNCLAIM_ENDPOINT = uid => `/leads/${uid}/un-claim/`
const GENERATE_CLOSE_ENDPOINT = uid => `/leads/${uid}/close/`

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

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),

      onList: ApiFilter.create({ key: 'on_list' }),
      byList: ApiFilter.create({ key: 'by_list' }),
      rating: ApiFilter.create({ key: 'rating' }),
      byUser: ApiFilter.create({ key: 'by_user' }),
      orderBy: ApiFilter.create({ key: 'order_by' }),
      byAccount: ApiFilter.create({ key: 'by_account' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(LEADS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'LeadAPI.list error',
        }),
      )
    return promise
  }

  claim(uid) {
    const promise = apiClient()
      .post(GENERATE_CLAIM_ENDPOINT(uid))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.claim' }))
    return promise
  }

  unclaim(uid) {
    const promise = apiClient()
      .post(GENERATE_UNCLAIM_ENDPOINT(uid))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.unclaim' }))
    return promise
  }

  create(title, account, contacts) {
    let data = {
      title,
      account,
      notes: [],
      lists: [],
      linked_contacts: contacts,
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

  close(id, amount, contractID) {
    let data = {
      closing_amount: amount,
      contract: contractID,
    }
    const promise = apiClient()
      .post(GENERATE_CLOSE_ENDPOINT(id), data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.close' }))
    return promise
  }
}
