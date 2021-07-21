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
      const res = await this.client.post(AlertTemplateAPI.ENDPOINT, d)
      return this.cls.fromAPI(res.data)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.createAlertTemplate' })(e)
    }
  }
  async deleteAlertTemplate(id) {
    try {
      await this.client.delete(`${AlertTemplateAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }
  async testAlertTemplate(id) {
    try {
      await this.client.post(`${AlertTemplateAPI.ENDPOINT}${id}/test/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }
  async runAlertTemplateNow(id) {
    try {
      await this.client.post(`${AlertTemplateAPI.ENDPOINT}${id}/run-now/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.deleteAlertTemplate' })(e)
    }
  }

  async updateAlertTemplate(id, data) {
    const d = objectToSnakeCase(data)
    try {
      await this.client.patch(`${AlertTemplateAPI.ENDPOINT}${id}/`, d)
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
      await this.client.patch(`${AlertMessageTemplateAPI.ENDPOINT}${id}/`, d)
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
  async createOperand(data) {
    let formData = objectToSnakeCase(data)
    try {
      await this.client.post(`${AlertOperandAPI.ENDPOINT}`, formData)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.create' })(e)
    }
  }
  async delete(id) {
    try {
      await this.client.delete(`${AlertOperandAPI.ENDPOINT}${id}/`)
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
  async createConfig(data) {
    let formData = objectToSnakeCase(data)
    try {
      await this.client.post(`${AlertConfigAPI.ENDPOINT}`, formData)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.create' })(e)
    }
  }
  async delete(id) {
    try {
      await this.client.delete(`${AlertConfigAPI.ENDPOINT}${id}/`)
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

  async createGroup(data) {
    let formData = objectToSnakeCase(data)
    try {
      await this.client.post(`${AlertGroupAPI.ENDPOINT}`, formData)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.create' })(e)
    }
  }

  async delete(id) {
    try {
      await this.client.delete(`${AlertGroupAPI.ENDPOINT}${id}/`)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.delete' })(e)
    }
  }
}
