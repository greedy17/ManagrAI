import NotificationAPI from '@/services/notifications/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import Reminder from '@/services/reminders/'

const NOTIFICATION_TYPE_REMINDER = 'REMINDER'
const NOTIFICATION_TYPE_SYSTEM = 'SYSTEM'
const NOTIFICATION_TYPE_EMAIL = 'EMAIL'
const NOTIFICATION_TYPES = {
  reminder: NOTIFICATION_TYPE_REMINDER,
  system: NOTIFICATION_TYPE_SYSTEM,
  email: NOTIFICATION_TYPE_EMAIL,
}

export { NOTIFICATION_TYPES }

export default class Notification {
  static readOnlyFields = ['id']
  static api = NotificationAPI.create(Notification)

  _determineNotifType(type, data) {
    switch (type) {
      case NOTIFICATION_TYPE_EMAIL:
        return data
      case NOTIFICATION_TYPE_REMINDER:
        return data
      case NOTIFICATION_TYPE_SYSTEM:
        return data
    }
  }
  constructor({
    id = null,
    title = '',
    notificationType = null,
    notifiedAt = null,
    notifyAt = null,
    meta = null,
    resourceId = null,
    viewed = false,
  } = {}) {
    Object.assign(this, {
      id,
      title,
      notificationType,
      notifyAt,
      notifiedAt,
      meta: this._determineNotifType(notificationType, meta),
      resourceId,
      viewed,
    })
  }

  static create(opts) {
    return new Notification(opts)
  }
  static fromAPI(json) {
    return new Notification(objectToCamelCase(json))
  }
  static toAPI(json, fields = [], excludeFields = []) {
    let data = {}
    if (fields.length > 0) {
      fields.forEach(f => {
        data[f] = json[f]
      })
    } else {
      data = json
    }
    excludeFields = [...Notification.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })
    return objectToSnakeCase(data)
  }
}
