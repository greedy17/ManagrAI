import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadAPI from './api'

export default class Lead {
  static api = LeadAPI.create(Lead)

  constructor({
    id = '',
    title = '',
    amount = null,
    closingAmount = null,
    primaryDescription = '',
    secondaryDescription = '',
    rating = null,
    account = null,
    accountRef = null,
    createdBy = null,
    createdByRef = null,
    datetimeCreated = null,
    linkedContacts = null,
    lastUpdatedAt = null,
    lastUpdatedBy = null,
    status = '',
    forecast = '',
    forecastRef = null,
    claimedBy = null,
    claimedByRef = null,
  } = {}) {
    Object.assign(this, {
      id,
      title,
      amount,
      closingAmount,
      primaryDescription,
      secondaryDescription,
      rating,
      account,
      accountRef,
      createdBy,
      createdByRef,
      linkedContacts,
      lastUpdatedAt,
      lastUpdatedBy,
      status,
      forecast,
      forecastRef,
      claimedBy,
      claimedByRef,
      datetimeCreated,
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
