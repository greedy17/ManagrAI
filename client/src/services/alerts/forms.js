import Form, { FormArray, FormField } from '@thinknimble/tn-forms'

import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
  Validator,
} from '@thinknimble/tn-validators'

export class AlertOperandForm extends Form {
  static operandCondition = new FormField({})
  static operandField = new FormField({})
  static operandOperator = new FormField({})
  static operandValue = new FormField({})
}
export class AlertGroupForm extends Form {
  static groupCondition = new FormField({})
  static alertOperand = new FormArray({
    name: 'alertOperands',
    groups: [new AlertOperandForm()],
  })
}
export class AlertMessageTemplate extends Form {
  static bindings = new FormField({})
  static notification_text = new FormField({})
  static body = new FormField({})
}
export class AlertTemplateForm extends Form {
  static title = new FormField({})
  static resourceType = new FormField({})
  static occurences = new FormField({})
  static recipients = new FormField({})
  static alertGroup = new FormArray({
    name: 'alertGroups',
    groups: [new AlertGroupForm()],
  })
  // adding this as a form array to submit all as one form
  static alertMessage = new FormArray({
    name: 'alertMessages',
    groups: [new AlertMessageTemplate()],
  })
}
