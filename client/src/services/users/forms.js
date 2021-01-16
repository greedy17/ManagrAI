import Form, { FormField } from '@thinknimble/tn-forms'

export class UserRegistrationForm extends Form {
  static firstName = new FormField()
  static lastName = new FormField()
  static email = new FormField()
  static password = new FormField()
  static organizationName = new FormField()

  toAPI() {
    return {
      first_name: this.field.firstName.value,
      last_name: this.field.lastName.value,
      email: this.field.email.value,
      password: this.field.password.value,
      organization_name: this.field.organizationName.value,
    }
  }
}
