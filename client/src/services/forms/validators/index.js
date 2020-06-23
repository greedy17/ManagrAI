export default {
  required,
  minLength,
  mustMatch,
}

/********************************************************
 * @message: message to be displayed to the user
 * @field: sends full field for now, to get name and value
 *  might just be able to send the field it is applied to
 * ********************************************************/
export function required({ check = true, message = '' } = {}) {
  return function (field) {
    let error = { name: 'required', message: 'This is a Required Field' }
    let name = field.name
    let value = field.value
    let errors = field.errors
    if ((!value && check == true) || (value.length <= 0 && check == true)) {
      if (message.length > 0) {
        error.message = message
      }
      errors.push(error)
    }
    return errors
  }
}

export function minLength({ length = 0, message = '' } = {}) {
  return function (field) {
    let error = {
      name: 'minlength',
      message: 'Please Enter a Minimum of ' + length + ' Characters',
    }
    let name = field.name
    let value = field.value
    let errors = field.errors
    if (value.length < length) {
      if (message.lenth > 0) {
        error.message = message
      }
      errors.push(error)
    }
    return errors
  }
}
// ***** Currently if trying to validate on blur will validate whole form as it is a formlevel validator
export function mustMatch({ targetString, matcherString, message = '' } = {}) {
  // matcher is passed as a string and taken from the form group this is a formGroup level validator
  return function (formGroup) {
    let formFields = formGroup.fc
    let field = formFields[targetString]
    let matcher = formFields[matcherString]
    //matcher is the matcher value
    let error = { name: 'mustmatch', message: 'This field must match its matcher' }
    let name = field.name
    let value = field.value
    let errors = field.errors
    let matcherValue = matcher.Value
    if (matcherValue !== value) {
      if (message.length > 0) {
        error.message = message
      }
      errors.push(error)
    }
    return errors
  }
}
