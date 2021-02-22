import SlackAPI from './api'

export default class SlackOAuth {
  static api = SlackAPI.create(SlackOAuth)
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
  FORM_RESOURCES,
  FORM_TYPES,
  MEETING_REVIEW_REQUIRED_FIELDS,
}
