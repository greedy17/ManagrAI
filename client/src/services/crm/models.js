import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase } from '../utils'
import { ObjectFieldAPI } from './api'

export class ObjectField extends Model {
    static api = ObjectFieldAPI.create(ObjectField)
    static id = new fields.CharField({ readOnly: true })
    static crmObject = new fields.CharField()
    static apiName = new fields.CharField()
    static createable = new fields.BooleanField()
    static dataType = new fields.CharField()
    static label = new fields.CharField()
    static length = new fields.IntegerField()
    static reference = new fields.CharField()
    static referenceToInfos = new fields.Field()
    static updateable = new fields.BooleanField()
    static displayValue = new fields.CharField()
    static referenceDisplayLabel = new fields.CharField({ readOnly: true })
    static filterable = new fields.CharField({ readOnly: true })
    static order = new fields.IntegerField()
    static includeInRecap = new fields.Field()

    static fromAPI(json = {}) {
        return new ObjectField(objectToCamelCase(json))
    }
}

const INTEGER = 'INTEGER'
const STRING = 'STRING'
const DATE = 'DATE'
const DATETIME = 'DATETIME'
const DECIMAL = 'DECIMAL'
const BOOLEAN = 'BOOLEAN'
const EMAIL = 'EMAIL'

const INPUT_TYPE_MAP = {
    Currency: 'number',
    Int: 'number',
    Double: 'number',
    Long: 'number',
    TextArea: 'text',
    String: 'text',
    Date: 'number',
    DateTime: 'number',
}
const ALERT_DATA_TYPE_MAP = {
    Currency: DECIMAL,
    Double: DECIMAL,
    Int: INTEGER,
    Long: INTEGER,
    String: STRING,
    Date: DATE,
    DateTime: DATETIME,
    Picklist: STRING,
    TextArea: STRING,
    Boolean: BOOLEAN,
    Email: EMAIL,
}
export { INTEGER, STRING, DATE, DATETIME, DECIMAL, INPUT_TYPE_MAP, ALERT_DATA_TYPE_MAP }