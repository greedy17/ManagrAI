const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

// NOTE: Bruno(4-22-20): currently only formats to USD
export function currencyFilter(value) {
  if (!value) return formatter.format(0)
  return formatter.format(value)
}

export function currencyFilterNoCents(value) {
  if (!value) return formatter.format(0).split('.')[0]
  return formatter.format(value).split('.')[0]
}
