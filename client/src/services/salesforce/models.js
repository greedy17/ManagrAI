import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import SalesforceAPI, { SObjectFormBuilderAPI } from './api'

export default class Salesforce extends Model {
  static api = SalesforceAPI.create(Salesforce)
  static id = new fields.CharField({ readOnly: true })
  static objectFields = new fields.Field({ readOnly: true, default: () => [] })
}

export class SObjectField extends Model {
  static api = SObjectFormBuilderAPI.create(SObjectField)
  static id = new fields.CharField({ readOnly: true })
  static apiName = new fields.BooleanField()
  static custom = new fields.BooleanField()
  static createable = new fields.BooleanField()
  static dataType = new fields.CharField()
  static label = new fields.CharField()
  static length = new fields.IntegerField()
  static reference = new fields.CharField()
  static referenceToInfos = new fields.ArrayField()
  static updateable = new fields.BooleanField()
  static required = new fields.BooleanField()
  static unique = new fields.BooleanField()
  static value = new fields.CharField()
  static displayValue = new fields.CharField()
}

export class SObjectValidations extends Model {
  static api = SObjectFormBuilderAPI.create(SObjectField)
  static id = new fields.CharField({ readOnly: true })
  static integration_id = new fields.CharField({})
  static description = new fields.TextField()
  static message = new fields.TextField()
}
