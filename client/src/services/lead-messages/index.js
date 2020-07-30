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
    lead = null,
    leadRef = null,
    datetimeCreated = null,
  } = {}) {
    Object.assign(this, {
      id,
      createdBy,
      createdByRef,
      linkedContacts,
      linkedContactsRef: linkedContactsRef.map(objectToCamelCase),
      messageId,
      direction,
      body,
      status,
      lead,
      leadRef,
      datetimeCreated,
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
