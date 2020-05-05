import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ListAPI from './api'

export default class List {
  static api = ListAPI.create(List)

  constructor({ id = '' } = {}) {
    Object.assign(this, {
      id,
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
