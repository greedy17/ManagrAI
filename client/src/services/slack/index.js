import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import SlackAPI from './api'
import { SObjectField } from '../salesforce'

export class SlackListResponse {
  constructor({ channels = [], responseMetadata = {} } = {}) {
    Object.assign(this, {
      channels: channels.map(channel => objectToCamelCase(channel)),
      nextCursor:
        responseMetadata['nextCursor'] && responseMetadata['nextCursor'].length
          ? responseMetadata['nextCursor']
          : null,
    })
  }

  static create(opts) {
    return new SlackListResponse(opts)
  }
  static fromAPI(json) {
    return new SlackListResponse(objectToCamelCase(json))
  }
}

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

  static fromAPI(obj) {
    // HACK WE USE A CUSTOM MANYTOMANY HERE SO WE NEED TO REORG

    let _refFields = obj['fields_ref'].map(ref => {
      return { ...ref['field_ref'], order: ref['order'], includeInRecap: ref['include_in_recap'] }
    })
    obj['fields_ref'] = _refFields

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
const LEAD = 'Lead'
const STAGE_GATING = 'STAGE_GATING'
const FORM_RESOURCES = [OPPORTUNITY, ACCOUNT, CONTACT, LEAD]
const FORM_TYPES = [MEETING_REVIEW, CREATE, UPDATE]
const MEETING_REVIEW_REQUIRED_FIELDS = {
  [ACCOUNT]: ['6407b7a1-a877-44e2-979d-1effafec5035', '0bb152b5-aac1-4ee0-9c25-51ae98d55af1', 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d', 'fae88a10-53cc-470e-86ec-32376c041893', 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'],
  [OPPORTUNITY]: ['6407b7a1-a877-44e2-979d-1effafec5035', '0bb152b5-aac1-4ee0-9c25-51ae98d55af1', 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d', 'fae88a10-53cc-470e-86ec-32376c041893', 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'],
  [LEAD]: ['6407b7a1-a877-44e2-979d-1effafec5035', '0bb152b5-aac1-4ee0-9c25-51ae98d55af1', 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d', 'fae88a10-53cc-470e-86ec-32376c041893', 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'],
  [CONTACT]: ['6407b7a1-a877-44e2-979d-1effafec5035', '0bb152b5-aac1-4ee0-9c25-51ae98d55af1', 'e286d1d5-5447-47e6-ad55-5f54fdd2b00d', 'fae88a10-53cc-470e-86ec-32376c041893', 'fd4207a6-fec0-4f0b-9ce1-6aaec31d39ed'],
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
