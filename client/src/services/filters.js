import moment from 'moment'

export { uppercase, momentDateTime, momentDateTimeShort, timeAgo, timeToNow }

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

export function formatDateShortWithTime(value) {
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
