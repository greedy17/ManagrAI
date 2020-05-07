import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

// API Endpoints
const CONTACTS_ENDPOINT = '/contacts/'

export default class ContactAPI {
  /**
   * Instantiate a new `ContactAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `ContactAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new ContactAPI(cls)
  }

  list({ pagination, filters }) {
    const filtersMap = {
      // Pagination
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      // Account
      account: ApiFilter.create({ key: 'account' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(CONTACTS_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'ContactAPI.list error',
        }),
      )
    return promise
  }

  create(firstName, lastName, email, phone, account) {
    // NOTE (Bruno 5-4-20): server-side does not yet include contact.position, so that is not being sent for now
    let data = {
      first_name: firstName,
      last_name: lastName,
      email,
      phone_number_1: phone,
      account,
    }
    const promise = apiClient()
      .post(CONTACTS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'ContactAPI.create' }))
    return promise
  }
}
