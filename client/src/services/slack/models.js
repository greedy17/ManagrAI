import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase } from '@thinknimble/tn-utils'

import SlackAPI from './api'

export default class SlackInstance extends Model {
  static api = SlackAPI.create(SlackInstance)

  static id = new fields.CharField()
  static organization = new fields.Field()
  static config = new fields.Field()
  static form_type = new fields.Field()
  static resource = new fields.Field()
  static stage = new fields.Field()
  static fields = new fields.Field()
  static fields_ref = new fields.Field()

  static fromAPI(json = {}) {
    return new SlackInstance(objectToCamelCase(json))
  }
}
