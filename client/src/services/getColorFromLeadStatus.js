const statusToPrimaryColor = {
  ready: '#FAB900',
  trial: '#9596B3',
  demo: '#88C9F9',
  waiting: '#9596B4',
  customer: '#2F9E54',
}

const statusToSecondaryColor = {
  ready: '#FEF1CD',
  trial: '#EFF0F5',
  demo: '#E8F4FE',
  waiting: '#EFEFF5',
  customer: '#D1ECDD',
}

function statusSlugger(status) {
  return status.toLowerCase()
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
