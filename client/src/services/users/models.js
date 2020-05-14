import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import UserAPI from './api'

export default class User {
  static api = UserAPI.create(User)

  constructor(user) {
    user = user || {}

    const {
      id = '',
      firstName = '',
      lastName = '',
      email = '',
      organization = null,
      organizationRef = null,
      accountsRef = null,
      state = null,
      type = null,
      fullName = null,
    } = user
    Object.assign(this, {
      id,
      firstName,
      lastName,
      email,
      organization,
      organizationRef,
      accountsRef,
      state,
      type,
      fullName,
    })
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
