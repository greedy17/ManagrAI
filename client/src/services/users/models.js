import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import UserAPI from './api'

export default class User {
  static api = UserAPI.create(User)
  static USER_TYPE_MANAGER = 'MANAGER'
  static USER_TYPE_REP = 'REP'
  static USER_TYPE_INTEGRATION = 'INTEGRATION'

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
      emailAuthLink = '',
      messageAuthAccount = null,
      messageAuthAccountRef = {},
      emailAuthAccount = {},
      emailAuthAccountRef = {},
      isStaff = false,
      quota = null,
      upside = null,
      commit = null,
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
      emailAuthLink,
      messageAuthAccount,
      messageAuthAccountRef,
      emailAuthAccount,
      emailAuthAccountRef,
      isStaff,
      quota,
      upside,
      commit,
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

  get emailConnected() {
    return this.emailAuthAccount && this.emailAuthAccountRef.accessToken
  }
  get textConnected() {
    return this.messageAuthAccount && this.messageAuthAccountRef.phoneNumber
  }
  get isManager() {
    return this.type && this.type == User.USER_TYPE_MANAGER
  }
}
