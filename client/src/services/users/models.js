import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase } from '@thinknimble/tn-utils'

import UserAPI from './api'
import { roles, types } from './constants'

export default class User extends Model {
  static api = UserAPI.create(User)
  static roles = roles
  static types = types

  static id = new fields.CharField()
  static firstName = new fields.CharField()
  static lastName = new fields.CharField()
  static email = new fields.CharField()
  static organization = new fields.Field()
  static organizationRef = new fields.Field()
  static salesforceAccount = new fields.Field()
  static salesforceAccountRef = new fields.Field()
  static accountsRef = new fields.Field()
  static state = new fields.Field()
  static type = new fields.Field()
  static fullName = new fields.Field()
  static emailAuthLink = new fields.CharField()
  static nylas = new fields.Field({ default: () => {} })
  static nylasRef = new fields.Field({ default: () => {} })
  static isStaff = new fields.BooleanField()
  static isAdmin = new fields.BooleanField()
  static isActive = new fields.BooleanField()
  static isInvited = new fields.BooleanField()
  static slackRef = new fields.Field()
  static zoomAccount = new fields.Field()
  static token = new fields.Field()
  static hasZoomIntegration = new fields.Field({ readOnly: true })
  static hasSalesforceIntegration = new fields.Field({ readOnly: true })
  static userLevel = new fields.Field({})

  static fromAPI(json = {}) {
    return new User(objectToCamelCase(json))
  }

  get emailConnected() {
    return this.nylas && this.nylasRef.accessToken
  }

  get textConnected() {
    return this.messageAuthAccount && this.messageAuthAccountRef.phoneNumber
  }

  get isManager() {
    return this.type && this.type == User.types.MANAGER
  }
}
