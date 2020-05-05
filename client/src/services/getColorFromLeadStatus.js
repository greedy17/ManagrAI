const statusToPrimaryColor = {
  ready: '#FAB900',
  trial: '#9596B3',
  demo: '#88C9F9',
  waiting: '#9596B4',
  customer: '#2F9E54',
  null: '#9596B4',
}

const statusToSecondaryColor = {
  ready: '#FEF1CD',
  trial: '#EFF0F5',
  demo: '#E8F4FE',
  waiting: '#EFEFF5',
  customer: '#D1ECDD',
  null: '#EFEFF5',
}

// must account for null status (as is the case on Lead creation)
function statusSlugger(status) {
  return status ? status.toLowerCase() : null
}

export function getStatusPrimaryColor(status) {
  let sluggedStatus = statusSlugger(status)
  return {
    backgroundColor: statusToPrimaryColor[sluggedStatus],
  }
}

export function getStatusSecondaryColor(status) {
  let sluggedStatus = statusSlugger(status)
  return {
    backgroundColor: statusToSecondaryColor[sluggedStatus],
  }
}
