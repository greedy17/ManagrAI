import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import SlackAPI from './api'
import { SObjectField } from '../salesforce'

export class CustomSlackForm extends Model {
  static api = null
  static id = new fields.CharField({ readOnly: true })
  static config = new fields.Field({
    defaultVal: () => {
      return { fields: [] }
    },
  })
  static formType = new fields.Field({})
  static resource = new fields.Field({})
  static stage = new fields.CharField({})
  static fieldsRef = new fields.ModelField({ ModelClass: SObjectField, many: true })
  static fields = new fields.ArrayField({ type: new fields.CharField(), defaultVal: [] })

  static fromApi(obj) {
    return CustomSlackForm.create(objectToCamelCase(obj))
  }
}
export default class SlackOAuth {
  static api = SlackAPI.create(SlackOAuth)
  static customSlackForm = CustomSlackForm
  static options = {
    WORKSPACE: 'WORKSPACE',
    USER: 'USER',
  }
  static redirectURI =
    window.location.protocol + '//' + window.location.host + '/settings/integrations'
}

const MEETING_REVIEW = 'MEETING_REVIEW'
const CREATE = 'CREATE'
const UPDATE = 'UPDATE'
const OPPORTUNITY = 'Opportunity'
const CONTACT = 'Contact'
const ACCOUNT = 'Account'
const STAGE_GATING = 'STAGE_GATING'
const FORM_RESOURCES = [OPPORTUNITY, ACCOUNT, CONTACT]
const FORM_TYPES = [MEETING_REVIEW, CREATE, UPDATE]
const MEETING_REVIEW_REQUIRED_FIELDS = {
  [ACCOUNT]: ['meeting_type', 'meeting_comments', 'sentiment'],
  [OPPORTUNITY]: [
    'meeting_type',
    'meeting_comments',
    'sentiment',
    'StageName',
    'ForecastCategoryName',
    'CloseDate',
    'Amount',
  ],
}
export {
  MEETING_REVIEW,
  CREATE,
  UPDATE,
  OPPORTUNITY,
  CONTACT,
  ACCOUNT,
  STAGE_GATING,
  FORM_RESOURCES,
  FORM_TYPES,
  MEETING_REVIEW_REQUIRED_FIELDS,
}
