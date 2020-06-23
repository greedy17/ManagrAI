import { objectToCamelCase } from '@thinknimble/tn-utils'

import LeadActivityLogAPI from './api'
import ActivityTypes from './types'

export default class LeadActivityLog {
  static api = LeadActivityLogAPI.create(LeadActivityLog)
  static types = ActivityTypes

  constructor({
    id = null,
    lead = null,
    leadRef = null,
    actionTimestamp = null,
    activity = null,
    actionTakenBy = null,
    actionTakenByRef = null,
    meta = {},
  } = {}) {
    Object.assign(this, {
      id,
      lead,
      leadRef,
      actionTimestamp,
      activity,
      actionTakenBy,
      actionTakenByRef,
      meta,
    })
  }

  static create(opts) {
    return new LeadActivityLog(opts)
  }

  static fromAPI(json) {
    return new LeadActivityLog(objectToCamelCase(json))
  }

  static toAPI(json, fields = [], excludeFields = []) {
    throw Error('LeadActivityLog.toAPI is not supported, because it is not writable')
  }

  clone() {
    return new LeadActivityLog(this)
  }

  get model() {
    return this.activity.split('.')[0]
  }

  get action() {
    return this.activity.split('.')[1]
  }
}
