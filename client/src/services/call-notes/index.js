import CallNoteAPI from '@/services/call-notes/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

export default class CallNote {
  static readOnlyFields = ['id']
  static api = CallNoteAPI.create(CallNote)

  constructor({
    id = null,
    datetimeCreated = null,
    lastEdited = null,
    title = '',
    content = '',
    updatedBy = null,
    createdFor = null,
    callDate = null,
  } = {}) {
    Object.assign(this, {
      id,
      datetimeCreated,
      title,
      lastEdited,
      content,
      updatedBy,
      createdFor,
      callDate,
    })
  }

  static create(opts) {
    return new CallNote(opts)
  }
  static fromAPI(json) {
    return new CallNote(objectToCamelCase(json))
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
    excludeFields = [...CallNote.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })
    return objectToSnakeCase(data)
  }
}
