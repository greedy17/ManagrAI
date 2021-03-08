import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import NylasAuthAccountAPI from './api'

export default class NylasAuthAccount {
  static api = NylasAuthAccountAPI.create(NylasAuthAccount)

  constructor({
    id = '',
    datetime_created = '',
    last_edited = '',
    access_token = '',
    account_id = '',
    email_address = '',
    provider = '',
    sync_state = '',
    name = '',
    linked_at = '',
    user = '',
  } = {}) {
    Object.assign(this, {
      id,
      datetime_created,
      last_edited,
      access_token,
      account_id,
      email_address,
      provider,
      sync_state,
      name,
      linked_at,
      user,
    })
  }

  static create(opts) {
    return new NylasAuthAccount(opts)
  }

  static fromAPI(json) {
    return new NylasAuthAccount(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new NylasAuthAccount(this)
  }
}
