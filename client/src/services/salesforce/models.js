import Model, { fields } from '@thinknimble/tn-models'
import models from '@thinknimble/tn-models/lib/models'
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
  static apiName = new fields.CharField()
  static custom = new fields.BooleanField()
  static createable = new fields.BooleanField()
  static dataType = new fields.CharField()
  static label = new fields.CharField()
  static length = new fields.IntegerField()
  static reference = new fields.CharField()
  static referenceToInfos = new fields.Field()
  static updateable = new fields.BooleanField()
  static required = new fields.BooleanField()
  static unique = new fields.BooleanField()
  static value = new fields.CharField()
  static displayValue = new fields.CharField()
  static referenceDisplayLabel = new fields.CharField({ readOnly: true })
}

export class SObjectValidation extends Model {
  static api = SObjectFormBuilderAPI.create(SObjectValidation)
  static id = new fields.CharField({ readOnly: true })
  static integration_id = new fields.CharField({})
  static description = new fields.CharField()
  static message = new fields.CharField()
}
// HACK:- PB quick class to use array fields
class SObjectPicklistValues extends Model {
  static label = new fields.CharField()
  static value = new fields.CharField()
}

export class SObjectPicklist extends Model {
  static api = SObjectFormBuilderAPI.create(SObjectPicklist)
  static id = new fields.CharField({ readOnly: true })
  static field = new fields.ArrayField({ type: SObjectField })
  static fieldRef = new fields.ModelField({ ModelClass: SObjectField })
  static values = new fields.ArrayField({ type: new fields.Field() })
}
