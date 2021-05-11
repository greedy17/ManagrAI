import Model, { fields } from '@thinknimble/tn-models'
import User from '../users/models'
import AlertTemplateAPI from './api'

export class AlertTemplateRef extends Model {
  /**
   * Template Ref class ignores Model Ref classes of child models
   * to avoid deep nested recurrsion
   */
  static id = new fields.IdField({ readOnly: true })
  static title = new fields.CharField()
  static user = new fields.CharField({})
  static isActive = new fields.BooleanField({ default: true })
  static resourceType = new fields.CharField({})
  //static groups = new fields.ArrayField({ type: AlertGroup })
  static messageTemplate = new fields.CharField({})
  static alertLevel = new fields.CharField({})
  //static configs = new fields.ArrayField({ type: AlertConfig })
  //static instances = new fields.ArrayField({ type: AlertInstance })
}

export class AlertGroupRef extends Model {
  static id = new fields.IdField({ readOnly: true })
  static groupCondition = new fields.CharField({})
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static groupOrder = new fields.IntegerField({})
  // operands = new fields.ArrayField({ type: AlertGroupOperand })
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
}

export class AlertGroup extends AlertGroupRef {
  static operandsRef = new fields.ModelField({ ModelClass: AlertGroupOperand, many: true })
  static newOperands = new fields.ModelField({ ModelClass: AlertGroupOperand, many: true })
}
export class AlertMessageTemplateRef extends Model {
  static id = new fields.IdField({ readOnly: true })
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static bindings = new fields.ArrayField({ type: new fields.CharField() })
  static notificationText = new fields.CharField({})
  static body = new fields.CharField({})
}
export class AlertMessageTemplate extends AlertTemplateRef {
  static id = new fields.IdField({ readOnly: true })
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static bindings = new fields.ArrayField({ type: new fields.CharField() })
  static notificationText = new fields.CharField({})
  static body = new fields.CharField({})
}

export class AlertConfig extends Model {
  static id = new fields.IdField({ readOnly: true })
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static recurrenceFrequency = new fields.IntegerField({})
  static recurrenceDay = new fields.IntegerField({})
  static recipients = new fields.ArrayField({ type: new fields.CharField() })
}

export class AlertInstance extends Model {
  static id = new fields.IdField({})
  static template = new fields.CharField({})
  static templateRef = new fields.ModelField({ ModelClass: AlertTemplateRef })
  static user = new fields.CharField({})
  static renderedText = new fields.CharField({})
  static resourceId = new fields.CharField({})
  static sentAt = new fields.CharField({})
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
}
