import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import EmailTemplateAPI from './api'

export default class EmailTemplate {
  static api = EmailTemplateAPI.create(EmailTemplate)

  static readOnlyFields = ['id']

  constructor({ id = '', user = '', userRef = {}, name = '', subject = '', bodyHtml = '' } = {}) {
    Object.assign(this, {
      id,
      user,
      userRef,
      name,
      subject,
      bodyHtml,
    })
  }

  static create(opts) {
    return new EmailTemplate(opts)
  }

  static fromAPI(json) {
    return new EmailTemplate(objectToCamelCase(json))
  }

  static toAPI(emailTemplate, fields = [], excludeFields = []) {
    // By default, send the whole object
    let data = {}

    // If it's a partial update, get only the fields specified
    if (fields.length > 0) {
      fields.forEach(field => {
        data[field] = emailTemplate[field]
      })
    } else {
      data = emailTemplate
    }

    //
    excludeFields = [...EmailTemplate.readOnlyFields, ...excludeFields]
    excludeFields.forEach(item => {
      delete data[item]
    })

    return objectToSnakeCase(data)
  }

  clone() {
    return new EmailTemplate(this)
  }
}
