const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

// NOTE: Bruno(4-22-20): currently only formats to USD
function currencyFilter(value) {
  if (!value) return ''
  return formatter.format(value)
}

export default currencyFilter
