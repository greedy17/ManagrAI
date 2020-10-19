import NotificationAPI from '@/services/notifications/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

const NOTIFICATION_TYPE_REMINDER = 'REMINDER'
const NOTIFICATION_TYPE_SYSTEM = 'SYSTEM'
const NOTIFICATION_TYPE_EMAIL = 'EMAIL'
const NOTIFICATION_TYPE_EMAIL_OPENED = 'EMAIL_OPENED'
const NOTIFICATION_TYPE_MESSAGE = 'MESSAGE'
const NOTIFICATION_TYPE_OPPORTUNITY = 'OPPORTUNITY'
const NOTIFICATION_TYPES = {
  [NOTIFICATION_TYPE_REMINDER]: { label: 'reminder', icon: 'alarm' },
  [NOTIFICATION_TYPE_SYSTEM]: { label: 'system', icon: 'dark-settings' },
  [NOTIFICATION_TYPE_EMAIL]: { label: 'email', icon: 'email' },
  [NOTIFICATION_TYPE_EMAIL_OPENED]: { label: 'email', icon: 'checkmark' },
  [NOTIFICATION_TYPE_MESSAGE]: { label: 'message', icon: 'sms' },
  [NOTIFICATION_TYPE_OPPORTUNITY]: { label: 'opportunity', icon: 'flag' },
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
