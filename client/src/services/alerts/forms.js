import Form, { FormArray, FormField } from '@thinknimble/tn-forms'
import { stringRenderer } from '../utils'

import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
  Validator,
} from '@thinknimble/tn-validators'
import AlertTemplate from '.'

export class AlertConfigForm extends Form {
  static recurrenceFrequency = new FormField({ value: 'WEEKLY' })
  static recurrenceDay = new FormField({ validators: [new RequiredValidator()] })
  static recipients = new FormField({})
  // Keeping a private copy of the dropdown ref obj for later use
  static _recipients = new FormField({ value: null })

  get toAPI() {
    //overriding .value here to set recipients into an array for future support
    let val = {
      ...this.value,
      recipients: [this.value.recipients],
    }
    // object to snakecase side effect, will change var with _ into var without camelcase
    delete val['_recipients']
    return val
  }
}
export class AlertOperandForm extends Form {
  static operandCondition = new FormField({ value: 'AND' })
  static operandIdentifier = new FormField({ validators: [new RequiredValidator()] })
  static operandOperator = new FormField({ validators: [new RequiredValidator()] })
  static operandValue = new FormField({ validators: [new RequiredValidator()] })
  static operandType = new FormField({ value: 'FIELD' })
  static operandOrder = new FormField({ value: 0, validators: [new RequiredValidator()] })
  // Keeping a private copy of the dropdown ref obj for later use
  static _operandIdentifier = new FormField({ value: null })
  static _operandOperator = new FormField({ value: null })
  static _operandValue = new FormField({ value: null })
  get toAPI() {
    const originalValue = this.value
    return {
      // object to snakecase side effect, will change var with _ into var without camelcase
      operandCondition: originalValue.operandCondition,
      operandIdentifier: originalValue.operandIdentifier,
      operandOperator: originalValue.operandOperator,
      operandValue: originalValue.operandValue,
      operandType: originalValue.operandType,
      operandOrder: originalValue.operandOrder,
    }
  }
}
export class AlertGroupForm extends Form {
  static groupCondition = new FormField({ value: 'AND' })
  static groupOrder = new FormField({ value: 0, validators: [new RequiredValidator()] })
  static alertOperands = new FormArray({
    name: 'alertOperands',
    groups: [new AlertOperandForm()],
  })
  get toAPI() {
    const originalValue = this.value

    return {
      groupCondition: originalValue.groupCondition,
      newOperands: this.field.alertOperands.groups.map(o => o.toAPI),
      groupOrder: originalValue.groupOrder,
    }
  }
}
export class AlertMessageTemplateForm extends Form {
  static bindings = new FormField({})
  static notificationText = new FormField({})
  static body = new FormField({ validators: [new RequiredValidator()] })
}
export class AlertTemplateForm extends Form {
  static title = new FormField({ validators: [new RequiredValidator()] })
  static resourceType = new FormField({ validators: [new RequiredValidator()] })
  static isActive = new FormField({ value: false })
  static alertLevel = new FormField({ value: 'ORGANIZATION' })
  static alertGroups = new FormArray({
    name: 'alertGroups',
    groups: [new AlertGroupForm()],
  })
  // adding this as a form array to submit all as one form
  static alertMessages = new FormArray({
    name: 'alertMessages',
    groups: [new AlertMessageTemplateForm()],
  })
  static alertConfig = new FormArray({
    name: 'alertConfig',
    groups: [new AlertConfigForm()],
  })
  // // Keeping a private copy of the dropdown ref obj for later use
  static _resourceType = new FormField({ value: null })

  reset() {
    return new AlertTemplateForm()
  }

  get toAPI() {
    const originalValue = this.value
    const bindings = stringRenderer('{', '}', originalValue.alertMessages[0].body)

    return {
      title: originalValue.title,
      isActive: originalValue.isActive,
      resourceType: originalValue.resourceType,
      // HACK - Forms Service does not support child form so we use FormArray
      messageTemplate: { ...originalValue.alertMessages[0], bindings },
      alertLevel: originalValue.alertLevel,
      newGroups: this.field.alertGroups.groups.map(g => g.toAPI),
      newConfigs: this.field.alertConfig.groups.map(g => g.toAPI),
    }
  }
}
