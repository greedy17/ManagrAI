import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import StoryReportAPI from './api'

export default class StoryReport {
  static api = StoryReportAPI.create(StoryReport)

  constructor({
    id = '',
    data = null,
    datetimeCreated = null,
    datetimeGenerated = null,
    lastEdited = null,
    lead = null,
  } = {}) {
    Object.assign(this, {
      id,
      data,
      datetimeCreated,
      datetimeGenerated,
      lastEdited,
      lead,
    })
  }

  static create(opts) {
    return new StoryReport(opts)
  }

  static fromAPI(json) {
    return new StoryReport(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new StoryReport(this)
  }
}
