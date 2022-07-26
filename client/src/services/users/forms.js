import Form, { FormField } from '@thinknimble/tn-forms'
import {
  MustMatchValidator,
  EmailValidator,
  RequiredValidator,
  MinLengthValidator,
} from '@thinknimble/tn-validators'
import { MaxLengthValidator } from '../validators'
import moment from 'moment'

export class UserRegistrationForm extends Form {
  static fullName = new FormField({ validators: [new RequiredValidator()] })
  static email = new FormField({ validators: [new RequiredValidator(), new EmailValidator()] })
  static password = new FormField({
    validators: [
      new RequiredValidator(),
      new MinLengthValidator({ minLength: 8, message: 'Minimum Length of 8 required' }),
      new MaxLengthValidator({ maxLength: 50, message: 'Maximum Length of 50 characters' })
      // new PatternValidator(),
    ],
  })
  static confirmPassword = new FormField({ validators: [new RequiredValidator()] })
  static dynamicFormValidators = {
    confirmPassword: [new MustMatchValidator({ matcher: 'password' })],
  }
  static organizationName = new FormField({ validators: [new RequiredValidator()] })
  static role = new FormField({ validators: [new RequiredValidator()] })
  static timezone = new FormField({
    value: moment.tz.guess(),
    validators: [new RequiredValidator()],
  })

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
  static dynamicFormValidators = {
    confirmPassword: [new MustMatchValidator({ matcher: 'password' })],
  }
  static timezone = new FormField({
    value: moment.tz.guess(),
    validators: [new RequiredValidator()],
  })

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
  static role = new FormField()
  static userLevel = new FormField({ validators: [new RequiredValidator()] })
  static organization = new FormField({ validators: [new RequiredValidator()] })
  static slackId = new FormField()
  static email = new FormField()
}

export class UserLoginForm extends Form {
  static email = new FormField({ validators: [new RequiredValidator()] })

  static password = new FormField({ validators: [new RequiredValidator({})] })
}

export class UserSlackAccountForm extends Form {
  static slackAccount = new FormField()
}

export class UserProfileForm extends Form {
  static firstName = new FormField({ validators: [new RequiredValidator()] })
  static lastName = new FormField({ validators: [new RequiredValidator()] })
  static timezone = new FormField({
    value: moment.tz.guess(),
    validators: [new RequiredValidator()],
  })
}



export class UserOnboardingForm extends Form {
  static onboarding = new FormField({ validators: [new RequiredValidator()] })
}

export { MustMatchValidator }
