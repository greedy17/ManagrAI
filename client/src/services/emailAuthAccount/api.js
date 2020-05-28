import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const EMAIL_AUTH_ACCOUNT_ENDPOINT = '/notes/'
export default class EmailAuthAccountAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new EmailAuthAccountAPI(cls)
  }
}
