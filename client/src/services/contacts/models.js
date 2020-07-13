import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ContactAPI from './api'

export default class Contact {
  static api = ContactAPI.create(Contact)

  constructor({
    id = '',
    firstName = '',
    lastName = '',
    fullName = '',
    title = '',
    email = '',
    account = null,
    phoneNumber1 = '',
    phoneNumber2 = '',
  } = {}) {
    Object.assign(this, {
      id,
      firstName,
      lastName,
      fullName,
      title,
      email,
      account,
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
