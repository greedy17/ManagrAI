import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ActionAPI from './api'

export default class Action {
  static api = ActionAPI.create(Action)

  constructor({
    id = '',
    actionType = null,
    actionTypeRef = null,
    actionDetail = null,
    lead = null,
    leadRef = null,
  } = {}) {
    Object.assign(this, {
      id,
      actionType,
      actionTypeRef,
      actionDetail,
      lead,
      leadRef,
    })
  }

  static create(opts) {
    return new Action(opts)
  }

  static fromAPI(json) {
    return new Action(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new Action(this)
  }
}
