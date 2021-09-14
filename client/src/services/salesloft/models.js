import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import SalesloftAccountAPI from './api'

export default class SalesloftAccount extends Model {
  static api = SalesloftAccountAPI.create(SalesloftAccount)
  static id = new fields.CharField({ readOnly: true })

  static fromAPI(json) {
    return new SalesloftAccount(objectToCamelCase(json))
  }

  static toAPI(json, fields = [], excludedFields = []) {
    return objectToSnakeCase(json)
  }
}
