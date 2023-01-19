import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'
import { apiClient, apiErrorHandler } from '@/services/api'
import { objectToSnakeCase } from '@/services/utils'

export default class AlertTemplateAPI extends ModelAPI {
  static ENDPOINT = 'alerts/templates/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
    forPipeline: ApiFilter.create({ key: 'for_pipeline' }),
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
      apiErrorHandler({ apiName: 'AlertTemplateAPI.testAlertTemplate' })(e)
    }
  }
  async runAlertTemplateNow(id, from_workflow) {
    const fw = objectToSnakeCase(from_workflow)
    try {
      const res = await this.client.post(`${AlertTemplateAPI.ENDPOINT}${id}/run-now/`, { from_workflow: fw})
      return res
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.runAlertTemplateNow' })(e)
    }
  }

  async getAdminAlerts(id) {
    try {
      const res = await this.client.get(`${AlertTemplateAPI.ENDPOINT}admin/`, { params: { org_id: id }})
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertTemplateAPI.getAdminAlerts' })(e)
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
      const res = await this.client.post(`${AlertOperandAPI.ENDPOINT}`, formData)
      return this.cls.fromAPI(res.data)
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
export class RealTimeAlertConfigAPI extends ModelAPI {
  static ENDPOINT = 'alerts/real-time-configs/'
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
      const res = await this.client.post(`${RealTimeAlertConfigAPI.ENDPOINT}`, formData)
      return this.cls.fromAPI(res.data)
    } catch (e) {
      apiErrorHandler({ apiName: 'RealTimeAlertConfigAPI.createConfig' })(e)
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
      const res = await this.client.post(`${AlertConfigAPI.ENDPOINT}`, formData)
      return this.cls.fromAPI(res.data)
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.create' })(e)
    }
  }
  async getCurrentInstances(configId) {
    let formData = objectToSnakeCase(configId)

    try {
      const res = await this.client.get(`${AlertConfigAPI.ENDPOINT}/current-instances/`, { params: formData })
      return res
    } catch (e) {
      apiErrorHandler({ apiName: 'AlertGroupAPI.getCurrentInstances' })(e)
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
      const res = await this.client.post(`${AlertGroupAPI.ENDPOINT}`, formData)
      return this.cls.fromAPI(res.data)
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

const INSTANCES_ENDPOINT = 'alerts/instances/'

export class AlertInstanceAPI extends ModelAPI {
  static ENDPOINT = 'alerts/instances/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  list({ pagination, filters }) {
    const filtersMap = {
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      ordering: ApiFilter.create({ key: 'ordering' }),
      byParams: ApiFilter.create({ key: 'by_params' }),
      byConfig: ApiFilter.create({ key: 'by_config' }),
    }

    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...pagination, ...filters }),
    }

    const promise = apiClient()
      .get(INSTANCES_ENDPOINT, options)
      .then(response => response.data)
      .then(data => {
        return {
          ...data,
          results: data.results.map(this.cls.fromAPI),
        }
      })
      .catch(
        apiErrorHandler({
          apiName: 'InstanceAPI.list error',
        }),
      )
    return promise
  }
}



export class RealTimeAPI extends ModelAPI {
  static ENDPOINT = 'alerts/real-time/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
  get client() {
    return apiClient()
  }

  async createRealTimeAlert(data) {
    const d = objectToSnakeCase(data)

    try {
      const res = await this.client.post(RealTimeAPI.ENDPOINT, d)
      return this.cls.fromAPI(res.data)
    } catch (e) {
      apiErrorHandler({ apiName: 'RealTimeAPI.createRealTimeAlert' })(e)
    }
  }

}