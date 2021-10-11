import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import GongAccountAPI from './api'

export default class GongAccount extends Model {
  static api = GongAccountAPI.create(GongAccount)
  static id = new fields.CharField({ readOnly: true })

  static fromAPI(json) {
    return new GongAccount(objectToCamelCase(json))
  }

  static toAPI(json, fields = [], excludedFields = []) {
    return objectToSnakeCase(json)
  }
}
