import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import ZoomAccountAPI from './api'

export default class ZoomAccount extends Model {
  static api = ZoomAccountAPI.create(ZoomAccount)
  static id = new fields.CharField({ readOnly: true })

  static fromAPI(json) {
    return new ZoomAccount(objectToCamelCase(json))
  }

  static toAPI(json, fields = [], excludedFields = []) {
    return objectToSnakeCase(json)
  }
}
