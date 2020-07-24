import NotificationAPI from '@/services/notifications/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

const NOTIFICATION_TYPE_REMINDER = 'REMINDER'
const NOTIFICATION_TYPE_SYSTEM = 'SYSTEM'
const NOTIFICATION_TYPE_EMAIL = 'EMAIL'
const NOTIFICATION_TYPE_EMAIL_OPENED = 'EMAIL_OPENED'
const NOTIFICATION_TYPES = {
  reminder: NOTIFICATION_TYPE_REMINDER,
  system: NOTIFICATION_TYPE_SYSTEM,
  email: NOTIFICATION_TYPE_EMAIL,
  emailOpened: NOTIFICATION_TYPE_EMAIL_OPENED,
}

export { NOTIFICATION_TYPES }

export default class Notification {
  static readOnlyFields = ['id']
  static api = NotificationAPI.create(Notification)

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
      meta: objectToCamelCase(meta),
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
