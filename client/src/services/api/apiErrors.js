import Vue from 'vue'

/**
 * This function accepts any type of value and reduces it to a single
 * string. This is particularly useful for translating objects with
 * nested values into a string.
 **/
function toMessageString(data) {
  if (typeof data === 'string' || typeof data === 'number') {
    return `<h2>${String(data)}</h2>`
  } else if (data instanceof Array) {
    return '<h2>' + data.map(i => String(i)).join(', ') + '</h2>'
  } else if (data instanceof Object) {
    let message = ''
    for (var key in data) {
      message += '<h2>' + toMessageString(data[key]) + '</h2>'
    }
    return message
  }
}
/**
 * A generic handler for API Errors.
 *
 * Shows an alert-alert notification for response error codes.
 **/
export function apiErrorHandler({
  apiName = '',
  enable400Alert = false,
  enable500Alert = false,
  rethrowErrors = true,
} = {}) {
  return error => {
    const { response } = error
    // Console log for dev debug
    // eslint-disable-next-line no-console
    console.log(`${apiName} Error:`, error)

    // Show error to user
    if (response.status >= 400 && response.status < 500) {
      // Handle 4xx errors (probably bad user input)
      const { data } = response
      let message = '<h2>Error...</h2>'
      // Handle common error structures
      if (data.detail) {
        message += `<h2>${data.detail}</h2>`
      } else if (data.non_field_errors) {
        message += `<h2>${data.non_field_errors}</h2>`
      } else {
        message = toMessageString(data)
      }
      if (enable400Alert) {
        Vue.prototype.$Alert.alert({
          type: 'error',
          message,
          timeout: 6000,
        })
      }
      // Optionally re-raise for further optional error handling
      if (rethrowErrors) {
        throw error
      }

      return
    }

    if (enable500Alert) {
      // Generic handling for other errors (ex: 500 errors)
      Vue.prototype.$Alert.alert({
        type: 'error',
        message: '<h2>Error...</h2>' + '<h2>Something went wrong! Please try again later.</h2>',
        timeout: 6000,
      })
    }
    // Optionally re-raise for further optional error handling
    if (rethrowErrors) {
      throw error
    }
  }
}
