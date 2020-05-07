import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ForecastAPI from './api'

export default class Forecast {
  static api = ForecastAPI.create(Forecast)

  constructor({ id = '' } = {}) {
    Object.assign(this, {
      id,
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
