const statusToPrimaryColor = {
  ready: '#FAB900',
  trial: '#9596B3',
  demo: '#88C9F9',
  waiting: '#9596B4',
  closed: '#2F9E54',
  lost: '#9596B4',
  booked: 'rgba(165, 55, 253, 1)',
  null: '#9596B4',
}

const statusToSecondaryColor = {
  ready: '#FEF1CD',
  trial: '#EFF0F5',
  demo: '#E8F4FE',
  waiting: '#EFEFF5',
  closed: '#D1ECDD',
  lost: '#EFEFF5',
  booked: 'rgba(165, 55, 253, 0.5)', // using rgba and changing opacity rather than color
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
