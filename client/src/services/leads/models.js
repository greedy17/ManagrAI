import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadAPI from './api'

// Choices for Lead company_size field
const ONE_TO_FIFTY = '1-50'
const FIFTYONE_TO_TWOHUNDRED = '51-200'
const TWOHUNDREDONE_TO_FIVEHUNDRED = '201-500'
const FIVEHUNDREDONE_TO_ONETHOUSAND = '501-1000'
const ONETHOUSANDONE_TO_FIVETHOUSAND = '1001-5000'
const MORE_THAN_FIVETHOUSAND = '5000+'

// Choices for Lead industry field
const AGRICULTURE = 'AGRICULTURE'
const APPAREL = 'APPAREL'
const BANKING = 'BANKING'
const BIOTECHNOLOGY = 'BIOTECHNOLOGY'
const CHEMICALS = 'CHEMICALS'
const COMMUNICATIONS = 'COMMUNICATIONS'
const CONSTRUCTION = 'CONSTRUCTION'
const CONSULTING = 'CONSULTING'
const EDUCATION = 'EDUCATION'
const ELECTRONICS = 'ELECTRONICS'
const ENERGY = 'ENERGY'
const ENGINEERING = 'ENGINEERING'
const ENTERTAINMENT = 'ENTERTAINMENT'
const ENVIRONMENTAL = 'ENVIRONMENTAL'
const FINANCE = 'FINANCE'
const FOOD_AND_BEVERAGE = 'FOOD_AND_BEVERAGE'
const GOVERNMENT = 'GOVERNMENT'
const HEALTHCARE = 'HEALTHCARE'
const HOSPITALITY = 'HOSPITALITY'
const INSURANCE = 'INSURANCE'
const MACHINERY = 'MACHINERY'
const MANUFACTURING = 'MANUFACTURING'
const MEDIA = 'MEDIA'
const NOT_FOR_PROFIT = 'NOT_FOR_PROFIT'
const RECREATION = 'RECREATION'
const RETAIL = 'RETAIL'
const SHIPPING = 'SHIPPING'
const TECHNOLOGY = 'TECHNOLOGY'
const TELECOMMUNICATIONS = 'TELECOMMUNICATIONS'
const TRANSPORTATION = 'TRANSPORTATION'
const UTILITIES = 'UTILITIES'
// NOTE (Bruno 9-15-2020): the following choice is reused for other choice-sets, such as Lead type field
const OTHER = 'OTHER'

// Choices for Lead type field
const MQL = 'MQL'
const SQL = 'SQL'

// Choices for Lead competitor field
const YES = 'YES'
const NO = 'NO'

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

  static COMPANY_SIZE_CHOICES = [
    {
      value: ONE_TO_FIFTY,
      label: ONE_TO_FIFTY,
    },
    {
      value: FIFTYONE_TO_TWOHUNDRED,
      label: FIFTYONE_TO_TWOHUNDRED,
    },
    {
      value: TWOHUNDREDONE_TO_FIVEHUNDRED,
      label: TWOHUNDREDONE_TO_FIVEHUNDRED,
    },
    {
      value: FIVEHUNDREDONE_TO_ONETHOUSAND,
      label: FIVEHUNDREDONE_TO_ONETHOUSAND,
    },
    {
      value: ONETHOUSANDONE_TO_FIVETHOUSAND,
      label: ONETHOUSANDONE_TO_FIVETHOUSAND,
    },
    {
      value: MORE_THAN_FIVETHOUSAND,
      label: MORE_THAN_FIVETHOUSAND,
    },
  ]

  static INDUSTRY_CHOICES = [
    { value: AGRICULTURE, label: 'Agriculture' },
    { value: APPAREL, label: 'Apparel' },
    { value: BANKING, label: 'Banking' },
    { value: BIOTECHNOLOGY, label: 'Biotechnology' },
    { value: CHEMICALS, label: 'Chemicals' },
    { value: COMMUNICATIONS, label: 'Communications' },
    { value: CONSTRUCTION, label: 'Construction' },
    { value: CONSULTING, label: 'Consulting' },
    { value: EDUCATION, label: 'Education' },
    { value: ELECTRONICS, label: 'Electronics' },
    { value: ENERGY, label: 'Energy' },
    { value: ENGINEERING, label: 'Engineering' },
    { value: ENTERTAINMENT, label: 'Entertainment' },
    { value: ENVIRONMENTAL, label: 'Environmental' },
    { value: FINANCE, label: 'Finance' },
    { value: FOOD_AND_BEVERAGE, label: 'Food & Beverage' },
    { value: GOVERNMENT, label: 'Government' },
    { value: HEALTHCARE, label: 'Healthcare' },
    { value: HOSPITALITY, label: 'Hospitality' },
    { value: INSURANCE, label: 'Insurance' },
    { value: MACHINERY, label: 'Machinery' },
    { value: MANUFACTURING, label: 'Manufacturing' },
    { value: MEDIA, label: 'Media' },
    { value: NOT_FOR_PROFIT, label: 'Not for Profit' },
    { value: RECREATION, label: 'Recreation' },
    { value: RETAIL, label: 'Retail' },
    { value: SHIPPING, label: 'Shipping' },
    { value: TECHNOLOGY, label: 'Technology' },
    { value: TELECOMMUNICATIONS, label: 'Telecommunications' },
    { value: TRANSPORTATION, label: 'Transportation' },
    { value: UTILITIES, label: 'Utilities' },
    { value: OTHER, label: 'Other' },
  ]

  static TYPE_CHOICES = [
    { value: MQL, label: MQL },
    { value: SQL, label: SQL },
    { value: OTHER, label: 'Other' },
  ]

  static COMPETITOR_CHOICES = [
    { value: YES, label: 'Yes' },
    { value: NO, label: 'No' },
    { value: OTHER, label: 'Other' },
  ]

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
