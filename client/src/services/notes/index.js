import NoteAPI from '@/services/notes/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

export default class Note {
  static readOnlyFields = ['id']
  static api = NoteAPI.create(Note)

  constructor({
    id = null,
    datetimeCreated = null,
    lastEdited = null,
    title = '',
    content = '',
    updatedBy = null,
    createdFor = null,
  } = {}) {
    Object.assign(this, { id, datetimeCreated, title, lastEdited, content, updatedBy, createdFor })
  }

  static create(opts) {
    return new Note(opts)
  }
  static fromAPI(json) {
    return new Note(objectToCamelCase(json))
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
    excludeFields = [...Note.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })
    return objectToSnakeCase(data)
  }
}
