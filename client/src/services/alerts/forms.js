import Form, { FormArray, FormField } from '@thinknimble/tn-forms'

import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
  Validator,
} from '@thinknimble/tn-validators'

export class AlertConfigForm extends Form {
  static recurrenceFrequency = new FormField({ value: 'WEEKLY' })
  static recurrenceDay = new FormField({})
  static recipients = new FormField({ value: [] })
}
export class AlertOperandForm extends Form {
  static operandCondition = new FormField({ value: 'AND' })
  static operandField = new FormField({})
  static operandOperator = new FormField({})
  static operandValue = new FormField({})
  static operandType = new FormField({ value: 'FIELD' })
}
export class AlertGroupForm extends Form {
  static groupCondition = new FormField({ value: 'AND' })
  static alertOperands = new FormArray({
    name: 'alertOperands',
    groups: [new AlertOperandForm()],
  })
}
export class AlertMessageTemplate extends Form {
  static bindings = new FormField({})
  static notificationText = new FormField({})
  static body = new FormField({})
}
export class AlertTemplateForm extends Form {
  static title = new FormField({})
  static resourceType = new FormField({})
  static recipients = new FormField({})
  static alertGroups = new FormArray({
    name: 'alertGroups',
    groups: [new AlertGroupForm()],
  })
  // adding this as a form array to submit all as one form
  static alertMessages = new FormArray({
    name: 'alertMessages',
    groups: [new AlertMessageTemplate()],
  })
  static alertConfig = new FormArray({
    name: 'alertConfig',
    groups: [new AlertConfigForm()],
  })
  reset() {
    return new AlertTemplateForm()
  }
}
