import { ModelAPI, ApiFilter, Model } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToSnakeCase } from '@/services/utils'

export default class AlertTemplateAPI extends ModelAPI {
  static ENDPOINT = 'alerts/templates/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }
  async createAlertTemplate(data) {
    const d = objectToSnakeCase(data)

    try {
      const res = this.client.post(AlertTemplateAPI.ENDPOINT, d)
      return this.cls.fromAPI(res.data)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.createAlertTemplate' })
    }
  }
  async deleteAlertTemplate(id) {
    try {
      this.client.delete(`${AlertTemplateAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })
    }
  }
}
