import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ActionAPI from './api'

import Contact from '../contacts'
import User from '../users'


export default class Action {
  static api = ActionAPI.create(Action)
  static readOnlyFields = ['id', 'actionTypeRef', 'createdByRef', 'leadRef', 'linkedContactsRef']

  constructor({
    id = '',
    actionType = null,
    actionTypeRef = null,
    actionDetail = '',
    createdBy = null,
    createdByRef = null,
    lead = null,
    leadRef = null,
    linkedContacts = [],
    linkedContactsRef = [],
  } = {}) {
    Object.assign(this, {
      id,
      actionType,
      actionTypeRef,
      actionDetail,
      createdBy,
      createdByRef: User.create(createdByRef),
      lead,
      leadRef,
      linkedContacts,
      linkedContactsRef: linkedContactsRef.map(Contact.create),
    })
  }

  static create(opts) {
    return new Action(opts)
  }

  static fromAPI(json) {
    return new Action(objectToCamelCase(json))
  }

  static toAPI(obj, fields = [], excludeFields = []) {
    let data = {}

    if (fields.length > 0) {
      fields.forEach(f => {
        data[f] = obj[f]
      })
    } else {
      data = obj.clone()
    }

    excludeFields = [...Action.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })

    return objectToSnakeCase(data)
  }

  clone() {
    return new Action(this)
  }
}
