// User roles
export const LEADERSHIP = 'LEADERSHIP'
export const FRONTLINE_MANAGER = 'FRONTLINE_MANAGER'
export const ACCOUNT_EXEC = 'ACCOUNT_EXEC'
export const ACCOUNT_MANAGER = 'ACCOUNT MANAGER'
export const OPERATIONS = 'OPERATIONS'
export const ENABLEMENT = 'ENABLEMENT'
export const SALES = 'SALES'
export const PR = 'PR'
export const ROLE_CHOICES = [
  { key: SALES, name: 'Sales' },
  { key: PR, name: 'PR' },
  // { key: LEADERSHIP, name: 'Leadership' },
  // { key: FRONTLINE_MANAGER, name: 'Frontline Manager' },
  // { key: ACCOUNT_EXEC, name: 'Account Executive' },
  // { key: ACCOUNT_MANAGER, name: 'Account Manager' },
  // { key: OPERATIONS, name: 'Operations' },
  // { key: ENABLEMENT, name: 'Enablement' },
]
export const roles = {
  SALES,
  PR,
  LEADERSHIP,
  FRONTLINE_MANAGER,
  ACCOUNT_EXEC,
  ACCOUNT_MANAGER,
  OPERATIONS,
  ENABLEMENT,
  ROLE_CHOICES,
}

// User types
export const MANAGER = 'MANAGER'
export const REP = 'REP'
export const SDR = 'SDR'
export const INTEGRATION = 'INTEGRATION'
export const types = {
  MANAGER,
  REP,
  SDR,
  INTEGRATION,
}
