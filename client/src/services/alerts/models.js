import Model, { fields } from '@thinknimble/tn-models'
import User from '../users/models'
import { objectToCamelCase } from '../utils'
import AlertTemplateAPI, {
  AlertMessageTemplateAPI,
  AlertOperandAPI,
  AlertConfigAPI,
  AlertGroupAPI,
  RealTimeAPI,
} from './api'

export class AlertTemplateRef extends Model {
  /**
   * Template Ref class ignores Model Ref classes of child models
   * to avoid deep nested recurrsion
   */
  static id = new fields.IdField({ readOnly: true })
  static title = new fields.CharField()
  static user = new fields.CharField({})
  static isActive = new fields.BooleanField({ default: true })
  static alertLevel = new fields.CharField({})
  static resourceType = new fields.CharField({})
}

export class AlertGroupRef extends Model {
  static id = new fields.IdField({ readOnly: true })
  static groupCondition = new fields.CharField({})
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static groupOrder = new fields.IntegerField({})
  //
}
export class AlertGroupOperand extends Model {
  static id = new fields.IdField({ readOnly: true })
  static group = new fields.CharField({ readOnly: true })
  static groupRef = new fields.ModelField({ ModelClass: AlertGroupRef })
  static operandCondition = new fields.CharField({})
  static operandType = new fields.CharField({})
  static operandIdentifier = new fields.CharField({})
  static operandOperator = new fields.CharField({})
  static operandValue = new fields.CharField({})
  static operandOrder = new fields.IntegerField({})
  static dataType = new fields.CharField({})
  static operandIdentifierRef = new fields.Field({})
  static api = AlertOperandAPI.create(AlertGroupOperand)
}

export class AlertGroup extends AlertGroupRef {
  static operands = new fields.ArrayField({ type: new fields.CharField() })
  static operandsRef = new fields.ModelField({ ModelClass: AlertGroupOperand, many: true })
  static newOperands = new fields.ModelField({ ModelClass: AlertGroupOperand, many: true })
  static api = AlertGroupAPI.create(AlertGroup)
}
export class AlertMessageTemplate extends Model {
  static api = AlertMessageTemplateAPI.create(AlertMessageTemplate)
  static id = new fields.IdField({ readOnly: true })
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static bindings = new fields.ArrayField({ type: new fields.CharField() })
  static notificationText = new fields.CharField({})
  static body = new fields.CharField({})
}

export class AlertConfig extends Model {
  static api = new AlertConfigAPI(AlertConfig)
  static id = new fields.IdField({ readOnly: true })
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static recurrenceFrequency = new fields.CharField({})
  static recurrenceDay = new fields.IntegerField({})
  static recipients = new fields.ArrayField({ type: new fields.CharField() })
  static recipientType = new fields.CharField({})
  static alertTargetsRef = new fields.Field({})
  static recipientsRef = new fields.Field({})
}

export class AlertInstance extends Model {
  static id = new fields.IdField({})
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static user = new fields.CharField({})
  static renderedText = new fields.CharField({})
  static resourceId = new fields.CharField({})
  static sentAt = new fields.CharField({})
  static config = new fields.ModelField({ ModelClass: AlertConfig })
}

export default class AlertTemplate extends AlertTemplateRef {
  static api = AlertTemplateAPI.create(AlertTemplate)
  static isActive = new fields.BooleanField({ default: true })
  static groupsRef = new fields.ModelField({ ModelClass: AlertGroup, many: true })
  static newGroups = new fields.ModelField({ ModelClass: AlertGroup, many: true })
  static messageTemplateRef = new fields.ModelField({ ModelClass: AlertMessageTemplate })
  static configsRef = new fields.ModelField({ ModelClass: AlertConfig, many: true })
  static newConfigs = new fields.ModelField({ ModelClass: AlertConfig, many: true })
  static instancesRef = new fields.ModelField({ ModelClass: AlertInstance, many: true })
  static groups = new fields.ArrayField({ type: new fields.CharField() })
  static configs = new fields.ArrayField({ type: new fields.CharField() })
  static instances = new fields.ArrayField({ type: new fields.CharField() })
}
export class RealTime extends Model {
  static api = RealTimeAPI.create(RealTime)
  static title = new fields.CharField()
  static resourceType = new fields.CharField({})
  static isActive = new fields.BooleanField({ default: true })
  static recipients = new fields.ArrayField({ type: new fields.CharField() })
  static pipelines = new fields.ArrayField({ type: new fields.CharField() })
  static config = new fields.CharField({})
}
