import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import OutreachAccountAPI from './api'

export default class OutreachAccount extends Model {
  static api = OutreachAccountAPI.create(OutreachAccount)
  static id = new fields.CharField({ readOnly: true })

  static fromAPI(json) {
    return new OutreachAccount(objectToCamelCase(json))
  }

  static toAPI(json, fields = [], excludedFields = []) {
    return objectToSnakeCase(json)
  }
}
