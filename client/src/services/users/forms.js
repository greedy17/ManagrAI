import Form, { FormField } from '@thinknimble/tn-forms'
import Model, { fields } from '@thinknimble/tn-models'
import { RequiredValidator, MustMatchValidator, Validator } from '@thinknimble/tn-validators'
import * as EmailValidatorObj from 'email-validator'
export class EmailValidator extends Validator {
  constructor({ message = 'Please Enter a Valid Email', code = 'invalidEmail' } = {}) {
    super({ message, code })
  }

  call(value) {
    if (typeof value === 'object') {
      throw new Error('Invalid value supplied')
    }
    try {
      console.log(value)
      EmailValidatorObj.validate(value)
    } catch {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    }
  }
}

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
      firstName: firstName,
      lastName: lastName,
      ...this.value,
      /* email: this.field.email.value,
      password: this.field.password.value,
      organization_name: this.field.organizationName.value,
      role: this.field.role.value, */
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
      firstName: firstName,
      lastName: lastName,
      ...this.value,
    }
  }
}

export class UserInviteForm extends Form {
  static email = new FormField({ validators: [new RequiredValidator(), new EmailValidator()] })
  static confirmEmail = new FormField({ validators: [new RequiredValidator()] })
  static role = new FormField({ validators: [] })
  static userLevel = new FormField({ validators: [new RequiredValidator()] })
  static organization = new FormField({ validators: [new RequiredValidator()] })

  dynamicValidators() {
    /**
     * helper method to add dynamic validators
     *
     * */

    this.addValidator(
      'confirmEmail',
      new MustMatchValidator({
        matcher: this.field['email'],
        message: 'Emails do not match',
      }),
    )
  }
  reset() {
    this.field.email.value = ''
    this.field.confirmEmail.value = ''
  }
}

export { MustMatchValidator }
