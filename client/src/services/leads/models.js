import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import LeadAPI from './api'

export default class Lead {
  static api = LeadAPI.create(Lead)

  constructor(lead) {
    lead = lead || {}

    // TODO(Bruno 4-9-20): fill out constructor based on this app's user properties
    // const {
    //   id = '',
    // } = lead
    // Object.assign(this, {
    //   id,
    // })
  }

  static create(opts) {
    return new Lead(opts)
  }

  static fromAPI(json) {
    return new Lead(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Lead(this)
  }
}
