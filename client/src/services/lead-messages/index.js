import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadMessageAPI from './api'

export default class LeadMessage {
  static api = LeadMessageAPI.create(LeadMessage)
  constructor({
    id = null,
    createdBy = '',
    createdByRef = '',
    linkedContacts = [],
    linkedContactsRef = [],
    messageId = null,
    direction = null,
    body = '',
    status = null,
  } = {}) {
    Object.assign(this, {
      id,
      createdBy,
      createdByRef,
      linkedContacts,
      linkedContactsRef,
      messageId,
      direction,
      body,
      status,
    })
  }

  static create(opts) {
    return new LeadMessage(opts)
  }
  static fromAPI(json) {
    return new LeadMessage(objectToCamelCase(json))
  }
  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }
}
