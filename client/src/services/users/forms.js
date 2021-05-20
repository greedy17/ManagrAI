import Form, { FormField } from '@thinknimble/tn-forms'
import Model, { fields } from '@thinknimble/tn-models'
import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
  Validator,
} from '@thinknimble/tn-validators'

export class UserRegistrationForm extends Form {
  static fullName = new FormField({ validators: [new RequiredValidator()] })
  static email = new FormField({ validators: [new RequiredValidator(), new EmailValidator()] })
  static password = new FormField({
    validators: [
      new RequiredValidator(),
      new MinLengthValidator({ minLength: 10, message: 'Minimum Length of 10 required' }),
    ],
  })
  static confirmPassword = new FormField({ validators: [new RequiredValidator()] })
  static organizationName = new FormField({ validators: [new RequiredValidator()] })
  static role = new FormField({ validators: [new RequiredValidator()] })

  dynamicValidators() {
    /**
     * helper method to add dynamic validators
     *
     * */

    this.addValidator(
      'confirmPassword',
      new MustMatchValidator({
        matcher: this.field['password'],
        message: 'Passwords do not match',
      }),
    )
  }

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

export class RepRegistrationForm extends Form {
  static fullName = new FormField({ validators: [new RequiredValidator()] })
  static email = new FormField({ validators: [new RequiredValidator(), new EmailValidator()] })
  static password = new FormField({
    validators: [
      new RequiredValidator(),
      new MinLengthValidator({ minLength: 10, message: 'Minimum Length of 10 required' }),
    ],
  })
  static confirmPassword = new FormField({ validators: [new RequiredValidator()] })

  dynamicValidators() {
    /**
     * helper method to add dynamic validators
     *
     * */

    this.addValidator(
      'confirmPassword',
      new MustMatchValidator({
        matcher: this.field['password'],
        message: 'Passwords do not match',
      }),
    )
  }

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
  static confirmEmail = new FormField({
    validators: [new RequiredValidator()],
  })
  static role = new FormField({ validators: [new RequiredValidator()] })
  static userLevel = new FormField({ validators: [new RequiredValidator()] })
  static organization = new FormField({ validators: [new RequiredValidator()] })
  static slackInvite = new FormField({ value: false })

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
    this.field.slackInvite.value = false
  }
}

export class UserLoginForm extends Form {
  static email = new FormField({ validators: [new RequiredValidator()] })

  static password = new FormField({ validators: [new RequiredValidator({})] })
}

export { MustMatchValidator }
