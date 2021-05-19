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
  timeOnlyShort,
  toCapitalCase,
  momentDateShort,
  toNumberSuffix,
}

function uppercase(value) {
  if (!value) return ''
  return value.toUpperCase()
}
function toNumberSuffix(val) {
  // returns the suffix of numbers
  let value = parseInt(val)
  if (!Number.isInteger(value)) {
    return null
  }
  if (value < 10 || value > 20) {
    if (/0$/.test(String(value))) {
      return `${value}th`
    } else if (/1$/.test(String(value))) {
      return `${value}st`
    } else if (/2$/.test(String(value))) {
      return `${value}nd`
    } else if (/3$/.test(String(value))) {
      return `${value}3rd`
    }
  } else {
    return `${value}th`
  }
}
function momentDateTime(value) {
  if (!value) return ''
  return moment.unix(value).format('LLLL')
}
function momentDateShort(value) {
  if (!value) return ''
  return moment.unix(value).format('LLLL')
}

function momentDateTimeShort(value) {
  if (!value) return ''
  return moment.unix(value).format('LL')
}

function timeAgo(value) {
  if (!value) return ''
  return moment(value).fromNow()
}

function timeToNow(value) {
  if (!value) return 'N/A'
  return moment(value).toNow(true)
}
function timeOnlyShort(value) {
  return moment(value).format('HH:MM a')
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

function toCapitalCase(val) {
  if (val && val.length) {
    if (typeof val == 'string') {
      return val[0].toLowerCase() + val.substring(1).toLowerCase()
    }
  }
}
