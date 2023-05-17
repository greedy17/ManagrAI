// import Model, { fields } from '@thinknimble/tn-models'
// import { objectToCamelCase } from '@thinknimble/tn-utils'

import ConversationAPI from './api'
// import { roles, ROLE_CHOICES, types } from './constants'

export default class Conversation { //extends Model {
  static api = ConversationAPI.create(Conversation)
//   static roles = roles
//   static roleChoices = ROLE_CHOICES
//   static types = types

//   static id = ''
//   static title = ''
//   static messages = []

  constructor({
    id = '',
    title = '',
    messages = [],
  } = {}) {
    Object.assign(this, {
      id,
      title,
      messages
    })
  }

//   static id = new fields.CharField()
//   static firstName = new fields.CharField()
//   static lastName = new fields.CharField()
//   static email = new fields.CharField()
//   static organization = new fields.Field()
//   static organizationRef = new fields.Field()
//   static salesforceAccount = new fields.Field()
//   static salesforceAccountRef = new fields.Field()
//   static reminders = new fields.Field()

//   static state = new fields.Field()
//   static type = new fields.Field()
//   static fullName = new fields.Field()
//   static emailAuthLink = new fields.CharField()
//   static nylas = new fields.Field({ default: () => { } })
//   static nylasRef = new fields.Field({ default: () => { } })
//   static isStaff = new fields.BooleanField()
//   static isAdmin = new fields.BooleanField()
//   static isActive = new fields.BooleanField()
//   static isInvited = new fields.BooleanField()
//   static slackRef = new fields.Field()
//   static slackAccount = new fields.Field()
//   static hubspotAccount = new fields.Field()
//   static hubspotAccountRef = new fields.Field()
//   static hasHubspotIntegration = new fields.Field({ readOnly: true })
//   static crm = new fields.CharField()
//   static zoomRef = new fields.Field()
//   static zoomAccount = new fields.Field()
//   static token = new fields.Field()
//   static hasZoomIntegration = new fields.Field({ readOnly: true })
//   static hasSalesforceIntegration = new fields.Field({ readOnly: true })
//   static userLevel = new fields.Field({})
//   static role = new fields.Field({})
//   static timezone = new fields.CharField()
//   static salesloftAccount = new fields.Field()
//   static hasSalesloftIntegration = new fields.Field({ readOnly: true })
//   static gongAccount = new fields.Field()
//   static hasGongIntegration = new fields.Field({ readOnly: true })
//   static outreachAccount = new fields.Field()
//   static hasOutreachIntegration = new fields.Field({ readOnly: true })
//   static activatedTemplateRef = new fields.Field()
//   static onboarding = new fields.BooleanField()
//   static forecast = new fields.Field()
//   static activationLinkRef = new fields.Field()
//   static team = new fields.Field()
//   static isTeamLead = new fields.Field({ readOnly: true })


//   static fromAPI(json = {}) {
//     return new Conversation(objectToCamelCase(json))
//   }

//   get emailConnected() {
//     return this.nylas && this.nylasRef.accessToken
//   }

//   get textConnected() {
//     return this.messageAuthAccount && this.messageAuthAccountRef.phoneNumber
//   }

//   get isManager() {
//     return this.type && this.type == User.types.MANAGER
//   }
}