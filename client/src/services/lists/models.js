import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ListAPI from './api'

export default class List {
  static api = ListAPI.create(List)

  constructor({ id = '', title = '', leadCount = null } = {}) {
    Object.assign(this, {
      id,
      title,
      leadCount,
    })
  }

  static create(opts) {
    return new List(opts)
  }

  static fromAPI(json) {
    return new List(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new List(this)
  }
}
