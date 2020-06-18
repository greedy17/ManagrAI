import CallNoteAPI from '@/services/call-notes/api'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import Contact from '../contacts'

export default class CallNote {
  static readOnlyFields = ['id', 'linkedContactsRef', 'createdByRef', 'updatedByRef']
  static api = CallNoteAPI.create(CallNote)

  constructor({
    id = null,
    title = '',
    content = '',
    updatedBy = null,
    lastEdited = null,
    createdFor = null,
    updatedByRef = null,
    createdByRef = null,
    callDate = null,
    linkedContacts = [],
    linkedContactsRef = [],
  } = {}) {
    Object.assign(this, {
      id,
      title,
      content,
      updatedBy,
      createdFor,
      callDate,
      lastEdited,
      updatedByRef,
      createdByRef,
      linkedContacts,
      linkedContactsRef: linkedContactsRef.map(Contact.create),
    })
  }

  static create(opts = {}) {
    return new CallNote(opts)
  }

  static fromAPI(json = {}) {
    return new CallNote(objectToCamelCase(json))
  }

  clone() {
    return CallNote.create(this)
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

    excludeFields = [...CallNote.readOnlyFields, ...excludeFields]
    excludeFields.forEach(f => {
      delete data[f]
    })

    // HACK: Format callDate as a ISO-8601 datetime using the current
    //       timezone offset.
    if (data.callDate) {
      const tzOffset = (new Date()).getTimezoneOffset()
      data.callDate = `${data.callDate}T${tzOffset / 60}:00`
    }
    // END HACK

    return objectToSnakeCase(data)
  }
}
