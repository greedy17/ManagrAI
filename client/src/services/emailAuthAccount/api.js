import { apiClient } from '@/services/api'

export default class NylasAuthAccountAPI {
  constructor(cls) {
    this.cls = cls
  }
  get client() {
    return apiClient()
  }
  static create(cls) {
    return new NylasAuthAccountAPI(cls)
  }
}
