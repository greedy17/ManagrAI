const statusToPrimaryColor = {
  ready: '#FAB900',
  trial: '#D7D7DD',
  demo: '#fA646A',
  waiting: '#9596B4',
  customer: '#199E54',
}

const statusToSecondaryColor = {
  ready: '#FEF1CC',
  demo: '#FFE0E1',
  waiting: '#EFEFF5',
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
