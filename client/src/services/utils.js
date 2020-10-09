import isPlainObject from 'lodash.isplainobject'
import moment from 'moment'
require('moment-timezone')
/**
 * @module       utils
 * @description  Utility functions.
 *
 * @author  William Huster <william@aspire.is>
 */

/**
 * @module       utils
 * @description  ThinkNimble's commonly-used utility functions.
 *
 * @author  William Huster <william@thinknimble.com>
 */

const Utils = {
  toSnakeCase,
  toCamelCase,
  objectToCamelCase,
  objectToSnakeCase,
  isDefined,
  isNull,
  formatNumberAsUSD,
  formatDateShort,
  textToKabobCase,
  getSubdomain,
  removeDuplicates,
  capitalizeWord,
  debounce,
  getTimeZone,
  convertToRgba,
  loadEntireCollection,
  constantToCapitalized,
}

export default Utils

/**
 * True/False, the given value is defined.
 **/

export function getTimeZone() {
  let localDateTime = new Date()
  let offset = localDateTime.getTimezoneOffset()
}

export function isDefined(value) {
  return typeof value !== 'undefined'
}

export function isNull(value) {
  return value === null
}

export function toSnakeCase(value) {
  let upperChars = value.match(/([A-Z])/g)

  if (!upperChars) {
    return value
  }

  let str = value.toString()
  for (let i = 0, n = upperChars.length; i < n; i++) {
    str = str.replace(new RegExp(upperChars[i]), '_' + upperChars[i].toLowerCase())
  }

  if (str.slice(0, 1) === '_') {
    str = str.slice(1)
  }

  return str
}

/**
 * Transform a string value from `snake_case` style notation to `camelCase` notation.
 * This is useful for translating Python-serialized JSON objects to JavaScript objects.
 *
 * @param {String} value - The string value to transform.
 */
export function toCamelCase(value) {
  if (value === value.toUpperCase()) return value

  return value
    .split('_')
    .map(function(word, index) {
      // Do nothing with the first word
      if (index === 0) {
        return word
      }
      // If it is not the first word only upper case the first char and lowercase the rest.
      return capitalizeWord(word)
    })
    .join('')
}

/**
 * Transform a string value from any style notation to `capitalize` notation.
 *
 * @param {String} word - The string value to transform.
 */
export function capitalizeWord(word) {
  return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
}

/**
 * Transform the string-based keys of a JavaScript object to `camelCase` style notation.
 * This is useful for translating the style of object keys after making an API call to
 * the Python-based API, which uses `snake_case` style notation by default.
 *
 * Works on both objects, arrays, and any combination of nested objects and arrays.
 */
export function objectToCamelCase(obj) {
  if (isObject(obj)) {
    return Object.keys(obj).reduce((acc, snakeKey) => {
      const camelKey = toCamelCase(snakeKey)
      acc[camelKey] = isObjectOrArray(obj[snakeKey])
        ? objectToCamelCase(obj[snakeKey])
        : obj[snakeKey]
      return acc
    }, {})
  }
  if (Array.isArray(obj)) {
    return obj.reduce((acc, val, index) => {
      acc[index] = isObjectOrArray(val) ? objectToCamelCase(val) : val
      return acc
    }, [])
  }
}

/**
 * Transform the string-based keys of a JavaScript object to `snake_case` style notation.
 * This is useful for translating the `camelCase` style of JavaScript keys BEFORE posting
 * the data to the Python-based API, which uses `snake_case` style notation by default.
 */
export function objectToSnakeCase(value) {
  if (isObject(value)) {
    return Object.keys(value).reduce((acc, camelKey) => {
      const snakeKey = toSnakeCase(camelKey)
      acc[snakeKey] = isObject(value[camelKey])
        ? objectToSnakeCase(value[camelKey])
        : value[camelKey]
      return acc
    }, {})
  }
}

/**
 * Check a value whether it is an Object
 */

export function isObject(value) {
  return value !== null && value instanceof Object && !Array.isArray(value)
}

/**
 * Check whether a value is an Object or Array
 */
export function isObjectOrArray(value) {
  return value !== null && value instanceof Object
}

/**
 *@function       debounce
 *@description    delay calling of callback function on set time
 *@params         callback <Function> : a function is being returned; time <Number> : delay time in milliseconds
 *@returns        {Function}
 */

export function debounce(callback, time) {
  let timer = null
  return function(...args) {
    const onComplete = () => {
      callback.apply(this, args)
      timer = null
    }

    if (timer) {
      clearTimeout(timer)
    }

    timer = setTimeout(onComplete, time)
  }
}

/**
 * Returns a alphabetically sorted array of Objects, sorted by a 'property' (String) and excluding a specified 'exception' (String)
 */
export function sortAlphabetically(arr, property, exception = null) {
  arr.sort(function(a, b) {
    if (a[property] !== exception && b[property] !== exception) {
      var textA = a[property].toUpperCase()
      var textB = b[property].toUpperCase()
      return textA < textB ? -1 : textA > textB ? 1 : 0
    }
  })
  return arr
}

/**
 * @function    getSubdomain
 * parses subdomain from window.location.hostname
 */
export function getSubdomain() {
  let hostnameArr = window.location.hostname.split('.')
  return hostnameArr.length === 3 ? hostnameArr[0] : 'n/a'
}

/**
 * @function    textToKabobCase
 * Takes a string of text (e.g. 'Financial Health') and turns it into its kabob-case counterpart (e.g. 'financial-health')
 * @param   {String}  text  - custom string that functions as action being tracked
 **/
export function textToKabobCase(text) {
  return text.toLowerCase().replace(' ', '-')
}

/**
 * Format a number as US Dollars
 *
 * @param {String, Number} value - The value to format as US Dollars
 */
export function formatNumberAsUSD(value) {
  // Ignore falsey values, except zero, because zero dollars is OK!
  if (value !== 0 && !value) return ''
  return Number(value).toLocaleString('en', {
    style: 'currency',
    currency: 'USD',
  })
}

/**
 * Format a Date string or object.
 *
 * Returns 'N/A' if a falsey value is given.
 *
 * @param {String, Date} value - The date string or object to format.
 */
export function formatDateShort(value) {
  if (!value) return 'N/A'
  const date = new Date(value)
  return date.toLocaleDateString(['en-US'], {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
  })
}

export function removeDuplicates(array) {
  let errorFields = array.reduce((acc, curr) => {
    if (acc.length <= 0) {
      acc.push({ name: curr.name, message: curr.message })
      return acc
    } else {
      let index = acc.findIndex(e => e.name === curr.name)
      if (index >= 0) {
        return acc
      } else {
        acc.push({ name: curr.name, errors: curr.message })
        return acc
      }
    }
  }, [])
  return errorFields
}

function convertToRgba(color, opacity = 1) {
  let red = ''
  let green = ''
  let blue = ''

  color = color.replace('#', '')
  if (color.length != 3) {
    for (let i = 0; i < color.length; i++) {
      if (i < 2) {
        red += color.substr(i, 1)
      }
      if (i > 1 && i < 4) {
        green += color.substr(i, 1)
      }
      if (i > 3 && i < 6) {
        blue += color.substr(i, 1)
      }
    }
  } else {
    // 3 digit hex codes are considered shorthand for 6 digit hex code
    for (let i = 0; i < color.length; i++) {
      if (i == 0) {
        red += color.substr(i, 1)
      }
      if (i > 0 && i < 2) {
        green += color.substr(i, 1)
      }
      if (i > 1 && i < 3) {
        blue += color.substr(i, 1)
      }
    }
  }
  if (red) {
    red = parseInt(red, 16)
  } else {
    red = 0
  }
  if (green) {
    green = parseInt(green, 16)
  } else {
    green = 0
  }
  if (blue) {
    blue = parseInt(blue, 16)
  } else {
    blue = 0
  }
  return `rgba(${red}, ${green}, ${blue}, ${opacity})`
}

/**
 * @function    loadEntireCollection
 * Since the list of collection is for populating a dropdown, there is no pagination UI.
 * Yet, our backend delivers paginated results.
 * Therefore, continue to retrieve (and append) more results as long as this collection has a next page.
 * @param   {CollectionManager}  collection  - the collection for which all pages should be loaded.
 **/

export async function loadEntireCollection(collection) {
  await collection.refresh()
  while (collection.pagination.hasNextPage) {
    await collection.addNextPage()
  }
}

export function constantToCapitalized(value) {
  if (!value) return ''
  return value
    .split('_')
    .map(capitalizeWord)
    .join(' ')
}
