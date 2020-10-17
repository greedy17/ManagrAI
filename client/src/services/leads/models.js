import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadAPI from './api'
import { COMPANY_SIZE_CHOICES, INDUSTRY_CHOICES, TYPE_CHOICES, COMPETITOR_CHOICES } from './options'

export default class Lead {
  static api = LeadAPI.create(Lead)

  // Lead Statuses
  static READY = 'READY'
  static TRIAL = 'TRIAL'
  static DEMO = 'DEMO'
  static WAITING = 'WAITING'
  static CLOSED = 'CLOSED'
  static LOST = 'LOST'
  static BOOKED = 'BOOKED'
  static LEAD = 'LEAD'

  static COMPANY_SIZE_CHOICES = COMPANY_SIZE_CHOICES
  static INDUSTRY_CHOICES = INDUSTRY_CHOICES
  static TYPE_CHOICES = TYPE_CHOICES
  static COMPETITOR_CHOICES = COMPETITOR_CHOICES

  constructor({
    id = '',
    title = '',
    amount = null,
    closingAmount = null,
    expectedCloseDate = null,
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
    filesRef = null,
    linkedContacts = null,
    linkedContactsRef = null,
    lastActionTaken = null,
    lastEdited = null,
    lastUpdatedBy = null,
    lastUpdatedByRef = null,
    status = null,
    statusRef = null,
    statusLastUpdate = null,
    forecast = null,
    forecastRef = null,
    claimedBy = null,
    claimedByRef = null,
    actions = null,
    actionsRef = null,
    lists = null,
    notes = null,
    companySize = null,
    industry = null,
    type = null,
    custom = null,
    competitor = null,
    competitorDescription = null,
    geographyAddress = null,
    geographyAddressComponents = null,
    latestScore = null,
    lastScore = null,
  } = {}) {
    Object.assign(this, {
      id,
      title,
      amount,
      closingAmount,
      expectedCloseDate,
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
      filesRef,
      linkedContacts,
      linkedContactsRef,
      lastActionTaken,
      lastEdited,
      lastUpdatedBy,
      lastUpdatedByRef,
      status,
      statusRef,
      statusLastUpdate,
      forecast,
      forecastRef,
      claimedBy,
      claimedByRef,
      actions,
      actionsRef,
      lists,
      notes,
      companySize,
      industry,
      type,
      custom,
      competitor,
      competitorDescription,
      geographyAddress,
      geographyAddressComponents,
      latestScore,
      lastScore,
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
