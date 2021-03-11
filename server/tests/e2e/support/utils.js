const LETTER_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
const INTEGER_CHARS = '0123456789'
const SYMBOL_CHARS = '!@#$%^&*()/?<>{}[]'
export function randomString({
  minLength = 0,
  maxLength = 50,
  fixedLength = null,
  include_integers = false,
  include_symbols = false,
} = {}) {
  let alphabet = (
    LETTER_CHARS +
    (include_integers ? INTEGER_CHARS : '') +
    (include_symbols ? SYMBOL_CHARS : '')
  )
  let result = ''
  const length = (
    fixedLength ||
    Math.max(Math.ceil(Math.random() * maxLength), minLength)
  )
  for (let i = 0; i < length; i++) {
    const charIndex = Math.floor(Math.random() * alphabet.length)
    result += alphabet[charIndex]
  }
  return result
}

export function randomNumber({
  maximum = 1000,
  integer = false,
  decimalPlaces = 2,
} = {}) {
  let result = Math.random() * maximum
  return integer ? Math.floor(result) : result.toFixed(decimalPlaces)
}