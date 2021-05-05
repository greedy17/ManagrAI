import Salesforce, { SObjectField, SObjectValidation, SObjectPicklist } from './models'

export default Salesforce
export { SObjectValidation, SObjectField, SObjectPicklist }
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
