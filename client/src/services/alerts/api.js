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
      apiErrorHandler({ apiName: 'AlertTemplateAPI.createAlertTemplate' })(e)
    }
  }
  async deleteAlertTemplate(id) {
    try {
      this.client.delete(`${AlertTemplateAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }
  async testAlertTemplate(id) {
    try {
      this.client.post(`${AlertTemplateAPI.ENDPOINT}${id}/test/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }
  async runAlertTemplateNow(id) {
    try {
      this.client.post(`${AlertTemplateAPI.ENDPOINT}${id}/run-now/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }

  async updateAlertTemplate(id, data) {
    const d = objectToSnakeCase(data)
    try {
      this.client.patch(`${AlertTemplateAPI.ENDPOINT}${id}/`, d)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.UpdateAlertTemplate' })(e)
    }
  }
}
export class AlertMessageTemplateAPI extends ModelAPI {
  static ENDPOINT = 'alerts/message-templates/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async updateMessageTemplate(id, data) {
    const d = objectToSnakeCase(data)
    try {
      this.client.patch(`${AlertMessageTemplateAPI.ENDPOINT}${id}/`, d)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.UpdateAlertTemplate' })(e)
    }
  }
}

export class AlertOperandAPI extends ModelAPI {
  static ENDPOINT = 'alerts/operands/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async delete(id) {
    try {
      this.client.delete(`${AlertOperandAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertOperandAPI.delete' })(e)
    }
  }
}
export class AlertConfigAPI extends ModelAPI {
  static ENDPOINT = 'alerts/configs/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async delete(id) {
    try {
      this.client.delete(`${AlertConfigAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertConfigAPI.delete' })(e)
    }
  }
}
export class AlertGroupAPI extends ModelAPI {
  static ENDPOINT = 'alerts/groups/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async delete(id) {
    try {
      this.client.delete(`${AlertGroupAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.delete' })(e)
    }
  }
}
