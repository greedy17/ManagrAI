import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadAPI from './api'

export default class Lead {
  static api = LeadAPI.create(Lead)

  constructor({
    id = '',
    title = '',
    amount = null,
    closingAmount = null,
    contract = null,
    primaryDescription = '',
    secondaryDescription = '',
    rating = null,
    account = null,
    accountRef = null,
    createdBy = null,
    createdByRef = null,
    datetimeCreated = null,
    files = null,
    linkedContacts = null,
    linkedContactsRef = null,
    lastEdited = null,
    lastUpdatedBy = null,
    lastUpdatedByRef = null,
    status = null,
    statusLastUpdate = null,
    forecast = null,
    forecastRef = null,
    claimedBy = null,
    claimedByRef = null,
    actions = null,
    actionsRef = null,
    lists = null,
    notes = null,
  } = {}) {
    Object.assign(this, {
      id,
      title,
      amount,
      closingAmount,
      contract,
      primaryDescription,
      secondaryDescription,
      rating,
      account,
      accountRef,
      createdBy,
      createdByRef,
      datetimeCreated,
      files,
      linkedContacts,
      linkedContactsRef,
      lastEdited,
      lastUpdatedBy,
      lastUpdatedByRef,
      status,
      statusLastUpdate,
      forecast,
      forecastRef,
      claimedBy,
      claimedByRef,
      actions,
      actionsRef,
      lists,
      notes,
    })
  }

  static create(opts) {
    return new Lead(opts)
  }

  static fromAPI(json) {
    return new Lead(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Lead(this)
  }
}
