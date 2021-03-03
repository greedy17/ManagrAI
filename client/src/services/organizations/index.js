import OrganizationAPI from '@/services/organizations/api'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'

export default class Organization {
  static readOnlyFields = ['id']
  static api = OrganizationAPI.create(Organization)

  constructor({ id = null, name = null, isExternalsyncenabled = false, slackRef = null } = {}) {
    Object.assign(this, {
      id,
      name,
      isExternalsyncenabled,
      slackRef,
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
