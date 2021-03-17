import Form, { FormField } from '@thinknimble/tn-forms'
import Model, { fields } from '@thinknimble/tn-models'
import { RequiredValidator } from '@thinknimble/tn-validators'

export class UserRegistrationForm extends Form {
  static fullName = new FormField({ validators: [new RequiredValidator()] })
  static email = new FormField({ validators: [new RequiredValidator()] })
  static password = new FormField({ validators: [new RequiredValidator()] })
  static organizationName = new FormField({ validators: [new RequiredValidator()] })
  static role = new FormField({ validators: [new RequiredValidator()] })

  toAPI() {
    const fullName = this.field.fullName.value
    const firstName = fullName.split(' ')[0]
    const lastName = fullName
      .split(' ')
      .slice(1)
      .join(' ')
    return {
      first_name: firstName,
      last_name: lastName,
      email: this.field.email.value,
      password: this.field.password.value,
      organization_name: this.field.organizationName.value,
      role: this.field.role.value,
    }
  }
}

export class RepRegistrationForm extends Form {
  static fullName = new FormField({ validators: [new RequiredValidator()] })
  static email = new FormField({ validators: [new RequiredValidator()] })
  static password = new FormField({ validators: [new RequiredValidator()] })

  toAPI() {
    const fullName = this.field.fullName.value
    const firstName = fullName.split(' ')[0]
    const lastName = fullName
      .split(' ')
      .slice(1)
      .join(' ')
    return {
      first_name: firstName,
      last_name: lastName,
      email: this.field.email.value,
      password: this.field.password.value,
    }
  }
}
