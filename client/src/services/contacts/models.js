import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ContactAPI from './api'

export default class Contact {
  static api = ContactAPI.create(Contact)

  constructor({
    id = '',
    firstName = '',
    lastName = '',
    fullName = '',
    email = '',
    account = null,
    title = '',
    phoneNumber1 = '',
    phoneNumber2 = '',
  } = {}) {
    Object.assign(this, {
      id,
      firstName,
      lastName,
      fullName,
      email,
      account,
      title,
      phoneNumber1,
      phoneNumber2,
    })
  }

  static create(opts) {
    return new Contact(opts)
  }

  static fromAPI(json) {
    return new Contact(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Contact(this)
  }
}
