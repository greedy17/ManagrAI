import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import SalesforceAPI from './api'

export default class Salesforce extends Model {
  static api = SalesforceAPI.create(Salesforce)
  static id = new fields.CharField({ readOnly: true })
  static objectFields = new fields.Field({ readOnly: true, default: () => [] })
}
