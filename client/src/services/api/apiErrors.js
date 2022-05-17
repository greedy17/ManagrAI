import Vue from 'vue'

import store from '../../store'

/**
 * This function accepts any type of value and reduces it to a single
 * string. This is particularly useful for translating objects with
 * nested values into a string.
 **/
function toMessageString(data, prefix = '') {
  if (typeof data === 'string' || typeof data === 'number') {
    return `<div>${prefix} ${String(data)}</div>`
  } else if (data instanceof Array) {
    return `<div>${prefix} ${data.map(i => String(i)).join(', ')}</div>`
  } else if (data instanceof Object) {
    let message = ''
    for (var key in data) {
      message += '<div>' + toMessageString(data[key], `${key}:`) + '</div>'
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
  enable400Alert = true,
  enable500Alert = true,
  rethrowErrors = true,
} = {}) {
  return error => {
    const { response } = error
    // Console log for dev debug
    // eslint-disable-next-line no-console
    console.log(`${apiName} Error:`, error)

    // Show error to user
    if (response && response.status >= 400 && response.status < 500 && response.status != 401) {
      // Handle 4xx errors (probably bad user input)
      const { data } = response

      let message = '<div>Error...</div>'
      // Handle common error structures
      if (data.detail) {
        message += `<div>${data.detail}</div>`
      } else if (data.non_field_errors) {
        message += `<div>${data.non_field_errors}</div>`
      } else {
        message = toMessageString(data)
      }
      if (enable400Alert) {
        Vue.prototype.$Alert.alert({
          type: 'error',
          message,
          timeout: 3000,
        })
      }
      // Optionally re-raise for further optional error handling
      if (rethrowErrors) {
        throw error
      }

      return
    }

    if (response && response.status === 401) {
      // Logs out a user if there is a 401 error
      store.commit('LOGOUT_USER')
      Vue.prototype.$Alert.alert({
        type: 'error',
        message: '<div>Error...</div>' + '<div>Invalid Token Please Login Again.</div>',
        timeout: 3000,
      })
    }

    // Optionally re-raise for further optional error handling
    if (rethrowErrors) {
      throw error
    }
  }
}
