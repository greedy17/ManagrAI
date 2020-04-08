import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import UserAPI from './api'

export default class User {
  static api = UserAPI.create(User)

  constructor(user) {
    user = user || {}

    // TODO(Bruno 4-8-20): fill out constructor based on this app's user properties
    // const {
    //   id = '',
    //   firstName = '',
    //   lastName = '',
    //   email = '',
    //   fullName = '',
    //   paypalEmail = '',
    //   birthYear = null,
    //   zipCode = null,
    //   isEmployee = null,
    //   isAdmin = null,
    //   isStaff = null,
    // } = user
    // Object.assign(this, {
    //   id,
    //   firstName,
    //   lastName,
    //   email,
    //   fullName,
    //   paypalEmail,
    //   birthYear,
    //   zipCode,
    //   isEmployee,
    //   isAdmin,
    //   isStaff,
    // })
  }

  static create(opts) {
    return new User(opts)
  }

  static fromAPI(json) {
    return new User(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new User(this)
  }
}
