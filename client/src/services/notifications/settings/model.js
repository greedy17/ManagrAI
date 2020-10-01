import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'
import { NotificationSettingsAPI } from './api'
class NotificationSelection {
  constructor({ id = null, option = null, user = null, value = false } = {}) {
    Object.assign(this, {
      id,
      option,
      user,
      value,
    })
  }
  static create(cls) {
    return new NotificationSelection(cls)
  }
  static fromAPI(json) {
    return NotificationSelection.create(objectToCamelCase(json))
  }
}

class NotificationOption {
  static NOTIFICATION_TYPE_ALERT = 'ALERT'
  static NOTIFICATION_TYPE_EMAIL = 'EMAIL'
  static NOTIFICATIONTYPES = [
    {
      label: 'Alert',
      value: this.NOTIFICATION_TYPE_ALERT,
    },
    {
      label: 'Email',
      value: this.NOTIFICATION_TYPE_EMAIL,
    },
  ]

  constructor({
    id = null,
    title = '',
    description = '',
    defaultValue = null,
    notificationType = null,
    value = new NotificationSelection(),
  } = {}) {
    Object.assign(this, {
      id,
      title,
      description,
      defaultValue,
      notificationType,
      value: NotificationSelection.create(NotificationSelection.fromAPI(value)),
    })
  }
  static create(cls) {
    return new NotificationOption(cls)
  }
  static fromAPI(json) {
    return new NotificationOption(objectToCamelCase(json))
  }
  static toAPI(json) {
    return objectToSnakeCase(json)
  }
}

export class NotificationSettings {
  static api = NotificationSettingsAPI.create(NotificationSettings)
  constructor({ options = [new NotificationOption()] } = {}) {
    Object.assign(this, {
      options: options,
    })
  }
  static fromAPI(json, cls) {
    switch (cls) {
      case 'option':
        return NotificationOption.fromAPI(json)

      case 'selection':
        return NotificationSelection.fromAPI(json)

      default:
        return objectToCamelCase(json)
    }
  }
}
