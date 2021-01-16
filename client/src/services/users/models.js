import Model, { fields } from '@thinknimble/tn-models'

import UserAPI from './api'

export default class User extends Model {
  static api = UserAPI.create(User)
  static USER_TYPE_MANAGER = 'MANAGER'
  static USER_TYPE_REP = 'REP'
  static USER_TYPE_INTEGRATION = 'INTEGRATION'

  static id = new fields.CharField()
  static firstName = new fields.CharField()
  static lastName = new fields.CharField()
  static email = new fields.CharField()
  static organization = new fields.Field()
  static organizationRef = new fields.Field()
  static salesforceAccount = new fields.Field()
  static accountsRef = new fields.Field()
  static state = new fields.Field()
  static type = new fields.Field()
  static fullName = new fields.Field()
  static emailAuthLink = new fields.CharField()
  static emailAuthAccount = new fields.Field({ default: () => {} })
  static emailAuthAccountRef = new fields.Field({ default: () => {} })
  static isStaff = new fields.BooleanField()
  static isAdmin = new fields.BooleanField()
  static slackRef = new fields.Field()
  static zoomAccount = new fields.Field()

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
