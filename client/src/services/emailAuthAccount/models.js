import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import EmailAuthAccountAPI from './api'

export default class EmailAuthAccount {
  static api = EmailAuthAccountAPI.create(EmailAuthAccount)

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
    return new EmailAuthAccount(opts)
  }

  static fromAPI(json) {
    return new EmailAuthAccount(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new EmailAuthAccount(this)
  }
}
