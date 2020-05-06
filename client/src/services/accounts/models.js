import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import AccountAPI from './api'

export default class Account {
  static api = AccountAPI.create(Account)

  constructor({
    id = '',
    name = '',
    url = '',
    type = null,
    state = null,
    organization = null,
  } = {}) {
    Object.assign(this, {
      id,
      name,
      url,
      type,
      state,
      organization,
    })
  }

  static create(opts) {
    return new Account(opts)
  }

  static fromAPI(json) {
    return new Account(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Account(this)
  }
}
