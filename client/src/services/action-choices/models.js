import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import ActionChoiceAPI from './api'

export default class ActionChoice {
  static api = ActionChoiceAPI.create(ActionChoice)

  constructor({
    id = '',
    datetimeCreated = null,
    lastEdited = null,
    title = '',
    description = '',
    organization = null,
  } = {}) {
    Object.assign(this, {
      id,
      datetimeCreated,
      lastEdited,
      title,
      description,
      organization,
    })
  }

  static create(opts) {
    return new ActionChoice(opts)
  }

  static fromAPI(json) {
    return new ActionChoice(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new ActionChoice(this)
  }
}
