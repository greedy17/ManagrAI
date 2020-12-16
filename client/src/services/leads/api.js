import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const LEADS_ENDPOINT = '/leads/'
const LEADS_COUNT_ENDPOINT = '/leads/count/'
const GENERATE_LEAD_ENDPOINT = uid => `/leads/${uid}/`
const GENERATE_CLAIM_ENDPOINT = uid => `/leads/${uid}/claim/`
const GENERATE_UNCLAIM_ENDPOINT = uid => `/leads/${uid}/un-claim/`
const GENERATE_CLOSE_ENDPOINT = uid => `/leads/${uid}/close/`
const DEMO_INACTIVE = 'demo/trigger-inactive/'
const DEMO_STALLED = 'demo/trigger-stalled/'
const DEMO_LATE = 'demo/trigger-late/'
const DEMO_CLOSE = 'demo/close-lead'

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
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      search: ApiFilter.create({ key: 'search' }),
      onList: ApiFilter.create({ key: 'on_list' }),
      byList: ApiFilter.create({ key: 'by_list' }),
      byRating: ApiFilter.create({ key: 'by_rating' }),
      byUser: ApiFilter.create({ key: 'by_user' }),
      orderBy: ApiFilter.create({ key: 'order_by' }),
      byAccount: ApiFilter.create({ key: 'by_account' }),
      byStatus: ApiFilter.create({ key: 'by_status' }),
      isClaimed: ApiFilter.create({ key: 'is_claimed' }),
      byScore: ApiFilter.create({ key: 'by_score' }),
      // by reps works like by user
      // setting this key because by_user is used in many places
      //byReps: ApiFilter.create({ key: 'by_reps' }),
    }
    if (filters.byReps) {
      filters.byUser = filters.byReps.toString()
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, {
        ...pagination,
        ...filters,
      }),
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
      .patch(GENERATE_LEAD_ENDPOINT(id), this.cls.toAPI(data))
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

  count(params) {
    let options = {
      params,
    }
    const promise = apiClient()
      .get(LEADS_COUNT_ENDPOINT, this.cls.toAPI(options))
      .then(response => response.data)
      .catch(apiErrorHandler({ apiName: 'LeadAPI.count' }))
    return promise
  }

  /***
   *
   *
   * FOR DEMO PURPOSES ONLY
   */

  clearLog(lead) {
    console.log(lead)
    const data = {
      lead: lead,
    }
    const promise = apiClient()
      .post(DEMO_INACTIVE, data)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'LeadAPI.list error',
        }),
      )
    return promise
  }
  stallInStage(lead) {
    const data = {
      lead: lead,
    }
    const promise = apiClient()
      .post(DEMO_STALLED, data)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
        }
      })
      .catch(e => console.log(e))

    return promise
  }
  delayCloseDate(lead, days) {
    const data = {
      lead: lead,
      days: days,
    }
    const promise = apiClient()
      .post(DEMO_LATE, data)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'LeadAPI.list error',
        }),
      )
    return promise
  }
  demoClose(id, amount) {
    let data = {
      lead: id,
      closing_amount: amount,
    }
    let url = `${DEMO_CLOSE}/`
    const promise = apiClient()
      .post(url, data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'LeadAPI.close' }))
    return promise
  }
}
