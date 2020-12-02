import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'
import Contact from '@/services/contacts'
import ZoomMeetingAPI from './api'

export default class ZoomMeeting extends Model {
  static api = ZoomMeetingAPI.create(ZoomMeeting)
  static id = new fields.CharField({ readOnly: true })
  static zoomAccount = new fields.CharField({ readOnly: true })
  static topic = new fields.CharField({ readOnly: true })
  static startTime = new fields.CharField({ readOnly: true })
  static timeZone = new fields.CharField({ readOnly: true })
  static participants = new fields.ModelField({
    modelClass: Contact,
    many: true,
  })
  static lead = new fields.CharField()
}
