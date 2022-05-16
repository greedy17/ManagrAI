import { apiClient, apiErrorHandler } from '@/services/api'

// API Endpoints
const EMAIL_TEMPLATE_ENDPOINT = '/email-templates/'
const GENERATE_EMAIL_TEMPLATE_ENDPOINT = uid => `/email-templates/${uid}/`

export default class EmailTemplateAPI {
  /**
   * Instantiate a new `EmailTemplateAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  constructor(cls) {
    this.cls = cls
  }

  /**
   * Factory method to create a new instance of `EmailTemplateAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  static create(cls) {
    return new EmailTemplateAPI(cls)
  }

  list() {
    const promise = apiClient()
      .get(EMAIL_TEMPLATE_ENDPOINT)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'EmailTemplateAPI.list error',
        }),
      )
    return promise
  }

  create(emailTemplate) {
    const data = this.cls.toAPI(emailTemplate)
    return apiClient()
      .post(EMAIL_TEMPLATE_ENDPOINT, data)
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'Create Email Template API error' }))
  }

  delete(emailTemplate) {
    return apiClient()
      .delete(GENERATE_EMAIL_TEMPLATE_ENDPOINT(emailTemplate.id))
      .then(response => this.cls.fromAPI(response.data))
      .catch(apiErrorHandler({ apiName: 'Delete Email Template API error' }))
  }
}
