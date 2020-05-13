import OrganizationAPI from '@/services/reminders/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

export default class Organization {
  static readOnlyFields = ['id']
  static api = OrganizationAPI.create(Organization)

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
    })
  }

  static create(opts) {
    return new Organization(opts)
  }
  static fromAPI(json) {
    return new Organization(objectToCamelCase(json))
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
    excludeFields = [...Organization.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })
    return objectToSnakeCase(data)
  }
}
