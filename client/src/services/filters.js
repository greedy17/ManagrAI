import moment from 'moment'

export { uppercase, momentDateTime, momentDateTimeShort, timeAgo, timeToNow, prependUrlProtocol }

function uppercase(value) {
  if (!value) return ''
  return value.toUpperCase()
}

function momentDateTime(value) {
  if (!value) return ''
  return moment.unix(value).format('LLLL')
}

function momentDateTimeShort(value) {
  if (!value) return ''
  return moment.unix(value).format('LLLL')
}

function timeAgo(value) {
  if (!value) return ''
  return moment(value).fromNow()
}

function timeToNow(value) {
  if (!value) return 'N/A'
  return moment(value).toNow(true)
}

function prependUrlProtocol(value) {
  if (!value) return ''
  if (!value.includes('http')) {
    value = 'https://' + value
  } else {
    if (!value.includes('https')) {
      let domainAndPath = link_url_from_params.split('://')[1]
      value = 'https://' + domainAndPath
    }
  }
  return value
}
