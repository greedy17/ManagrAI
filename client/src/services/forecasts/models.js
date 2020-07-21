import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ForecastAPI from './api'

export default class Forecast {
  static api = ForecastAPI.create(Forecast)
  static TODAY_ONWARD = 'TODAY_ONWARD'
  static TODAY = 'TODAY'
  static YESTERDAY = 'YESTERDAY'
  static THIS_WEEK = 'THIS_WEEK'
  static LAST_WEEK = 'LAST_WEEK'
  static THIS_MONTH = 'THIS_MONTH'
  static LAST_MONTH = 'LAST_MONTH'
  static THIS_QUARTER = 'THIS_QUARTER'
  static LAST_QUARTER = 'LAST_QUARTER'
  static THIS_YEAR = 'THIS_YEAR'
  static LAST_YEAR = 'LAST_YEAR'
  static ALL_TIME = 'ALL_TIME'

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
