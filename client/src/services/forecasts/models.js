import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ForecastAPI from './api'

export default class Forecast {
  static api = ForecastAPI.create(Forecast)

  // Date Range Presets
  static TODAY_ONWARD = 'TODAY_ONWARD'
  static TODAY = 'TODAY'
  static YESTERDAY = 'YESTERDAY'
  static THIS_WEEK = 'THIS_WEEK'
  static LAST_WEEK = 'LAST_WEEK'
  static THIS_MONTH = 'THIS_MONTH'
  static LAST_MONTH = 'LAST_MONTH'
  static NEXT_MONTH = 'NEXT_MONTH'
  static THIS_QUARTER = 'THIS_QUARTER'
  static LAST_QUARTER = 'LAST_QUARTER'
  static NEXT_QUARTER = 'NEXT_QUARTER'
  static THIS_YEAR = 'THIS_YEAR'
  static LAST_YEAR = 'LAST_YEAR'
  static ALL_TIME = 'ALL_TIME'

  // Forecast Types
  static FIFTY_FIFTY = '50/50'
  static STRONG = 'STRONG'
  static VERBAL = 'VERBAL'
  static FUTURE = 'FUTURE'
  static UNFORECASTED = 'UNFORECASTED'
  static NA = 'NA'
  static CLOSED = 'CLOSED'

  constructor({
    id = '',
    datetimeCreated = null,
    forecast = null,
    lastEdited = null,
    lead = null,
    leadRef = null,
  } = {}) {
    Object.assign(this, {
      id,
      datetimeCreated,
      forecast,
      lastEdited,
      lead,
      leadRef,
    })
  }

  static create(opts) {
    return new Forecast(opts)
  }

  static fromAPI(json) {
    return new Forecast(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Forecast(this)
  }
}
