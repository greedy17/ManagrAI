// import Model, { fields } from '@thinknimble/tn-models'
// import { objectToCamelCase } from '@thinknimble/tn-utils'

// import SlackAPI from './api'

// export default class SlackFormInstance extends Model {
//   static api = SlackAPI.create(SlackFormInstance)

//   static id = new fields.Field()
//   static workflow = new fields.Field()
//   static resource_id = new fields.Field()
//   static resource = new fields.Field()
//   static is_submitted = new fields.Field()
//   static submission_date = new fields.Field()
//   static update_source = new fields.Field()
//   static user = new fields.Field()
//   static template = new fields.Field()
//   static template_ref = new fields.Field()
//   static saved_data = new fields.Field()
//   static previous_data = new fields.Field()

//   static fromAPI(json = {}) {
//     return new SlackFormInstance(objectToCamelCase(json))
//   }
// }
