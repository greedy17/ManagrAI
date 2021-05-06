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
  static recurrenceDay = new FormField({ validators: [new RequiredValidator()] })
  static recipients = new FormField({})
  // Keeping a private copy of the dropdown ref obj for later use
  static _recipients = new FormField({ value: null })
}
export class AlertOperandForm extends Form {
  static operandCondition = new FormField({ value: 'AND' })
  static operandIdentifier = new FormField({ validators: [new RequiredValidator()] })
  static operandOperator = new FormField({ validators: [new RequiredValidator()] })
  static operandValue = new FormField({ validators: [new RequiredValidator()] })
  static operandType = new FormField({ value: 'FIELD' })
  // Keeping a private copy of the dropdown ref obj for later use
  static _operandIdentifier = new FormField({ value: null })
  static _operandOperator = new FormField({ value: null })
  static _operandValue = new FormField({ value: null })
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
  static body = new FormField({ validators: [new RequiredValidator()] })
}
export class AlertTemplateForm extends Form {
  static title = new FormField({ validators: [new RequiredValidator()] })
  static resourceType = new FormField({ validators: [new RequiredValidator()] })
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
  // // Keeping a private copy of the dropdown ref obj for later use
  static _resourceType = new FormField({ value: null })

  reset() {
    return new AlertTemplateForm()
  }
}
