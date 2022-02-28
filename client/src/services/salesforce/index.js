import Salesforce, { SObjectField, SObjectValidation, SObjectPicklist, SObjects } from './models'

export default Salesforce
export { SObjectValidation, SObjectField, SObjectPicklist, SObjects }
export const OPPORTUNITY = 'Opportunity'
export const CONTACT = 'Contact'
export const ACCOUNT = 'Account'
export const LEAD = 'Lead'
export const SOBJECTS_LIST = [
  { key: OPPORTUNITY, value: OPPORTUNITY },
  { key: ACCOUNT, value: ACCOUNT },
  { key: LEAD, value: LEAD },
  { key: CONTACT, value: CONTACT },
]

export const NON_FIELD_ALERT_OPTS = {
  [OPPORTUNITY]: [
    { referenceDisplayLabel: 'Last Stage Update', apiName: 'last_stage_update', dataType: 'Date' },
  ],
  [ACCOUNT]: [],
  [CONTACT]: [],
  [LEAD]: [],
}
