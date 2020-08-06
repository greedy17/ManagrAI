import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import StatusAPI from './api'

export default class Status {
  static api = StatusAPI.create(Status)

  constructor({
    id = '',
    datetimeCreated = null,
    lastEdited = null,
    title = '',
    description = '',
    organization = null,
    color = null,
  } = {}) {
    Object.assign(this, {
      id,
      datetimeCreated,
      lastEdited,
      title,
      description,
      organization,
      color,
    })
  }

  static create(opts) {
    return new Status(opts)
  }

  static fromAPI(json) {
    return new Status(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Status(this)
  }
}
