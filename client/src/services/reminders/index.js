import ReminderAPI from '@/services/reminders/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

export default class Reminder {
  static readOnlyFields = ['id']
  static api = ReminderAPI.create(Reminder)

  constructor({
    id = null,
    datetimeCreated = null,
    lastEdited = null,
    title = '',
    content = '',
    updatedBy = null,
    createdFor = null,
    completed = false,
    viewed = false,
    datetimeFor = null,
    createdByRef = null,
    updatedByRef = null,
  } = {}) {
    Object.assign(this, {
      id,
      datetimeCreated,
      title,
      lastEdited,
      content,
      updatedBy,
      createdFor,
      completed,
      viewed,
      datetimeFor,
      createdByRef,
      updatedByRef,
    })
  }

  static create(opts) {
    return new Reminder(opts)
  }
  static fromAPI(json) {
    return new Reminder(objectToCamelCase(json))
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
    excludeFields = [...Reminder.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })
    return objectToSnakeCase(data)
  }
}
