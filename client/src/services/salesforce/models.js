import Model, { fields } from '@thinknimble/tn-models'
import models from '@thinknimble/tn-models/lib/models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import SalesforceAPI, { SObjectFormBuilderAPI, SObjectValidationAPI } from './api'

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
  static order = new fields.IntegerField()

  static fromAPI(json = {}) {
    return new SObjectField(objectToCamelCase(json))
  }
}

export class SObjectValidation extends Model {
  static api = SObjectValidationAPI.create(SObjectValidation)
  static id = new fields.CharField({ readOnly: true })
  static integration_id = new fields.CharField({})
  static description = new fields.CharField()
  static message = new fields.CharField()

  static fromAPI(json = {}) {
    return new SObjectValidation(objectToCamelCase(json))
  }
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

const INTEGER = 'INTEGER'
const STRING = 'STRING'
const DATE = 'DATE'
const DECIMAL = 'DECIMAL'

const INPUT_TYPE_MAP = {
  Currency: 'number',
  Int: 'number',
  Double: 'number',
  Long: 'number',
  TextArea: 'text',
  String: 'text',
}
const ALERT_DATA_TYPE_MAP = {
  Currency: DECIMAL,
  Double: DECIMAL,
  Int: INTEGER,
  Long: INTEGER,
  String: STRING,
  Date: DATE,
  DateTime: DATE,
  Picklist: STRING,
  TextArea: STRING,
}
export { INTEGER, STRING, DATE, DECIMAL, INPUT_TYPE_MAP, ALERT_DATA_TYPE_MAP }
