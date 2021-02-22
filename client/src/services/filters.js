import moment from 'moment'
import { snakeCaseToText } from './utils'

export {
  uppercase,
  momentDateTime,
  momentDateTimeShort,
  timeAgo,
  timeToNow,
  prependUrlProtocol,
  formatDateShortWithTime,
  roundToOneDecimalPlace,
  snakeCaseToTextFilter,
}

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
      let domainAndPath = value.split('://')[1]
      value = 'https://' + domainAndPath
    }
  }
  return value
}

function formatDateShortWithTime(value) {
  if (!value) return 'N/A'
  const date = new Date(value)
  return date.toLocaleDateString(['en-US'], {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function roundToOneDecimalPlace(value) {
  // must be int, float, or their stringified versions
  if (isNaN(parseFloat(value))) {
    return NaN
  }
  return Math.round(parseFloat(value) * 10) / 10
}

function snakeCaseToTextFilter(value) {
  return snakeCaseToText(value)
}
