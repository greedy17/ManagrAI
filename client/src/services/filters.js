import moment from 'moment'
export { uppercase, momentDateTime, momentDateTimeShort }

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
