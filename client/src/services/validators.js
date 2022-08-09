export class Validator {
  /**
   * Crete an instance of the validator.
   * @param {string} message - The error message to return if validation fails.
   * @param {string} code - The code to return with the thrown Error if validation fails.
   */
  constructor({ message = 'Invalid value', code = 'invalid' } = {}) {
    Object.assign(this, { message, code })
  }

  /**
   * Perform validation on a given value.
   * @param {string|number|Array|Object} value - The error message to return if validation fails.
   */
  call(value) {
    throw new Error('Validator cannot be used directly, it must be overwritten in a subclass')
  }
}

export class RequiredValidator extends Validator {
  constructor({ message = 'This is a required field', code = 'required' } = {}) {
    super({ message, code })
  }
  call(value) {
    if (!value) {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    } else if (value) {
      if (Array.isArray(value) && !value.length) {
        throw new Error(JSON.stringify({ code: this.code, message: this.message }))
      } else if (!value.toString().length) {
        throw new Error(JSON.stringify({ code: this.code, message: this.message }))
      }
    }
  }
}

export class MaxLengthValidator extends Validator {
  constructor({
    message = 'Must be no greater than maximum length',
    code = 'maxLength',
    maxLength = 50,
  } = {}) {
    super({ message, code })
    this.maxLength = maxLength
  }

  call(value) {
    new RequiredValidator({ message: this.message, code: this.code }).call(value)
    if (!value || value.toString().length > this.maxLength) {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    }
  }
}

export class PatternValidator extends Validator {
  constructor({
    message = 'Value does not match pattern',
    code = 'invalidPattern',
    pattern = '',
  } = {}) {
    super({ message, code })
    this.pattern = typeof pattern == 'string' ? new RegExp(pattern) : pattern
  }
  call(value) {
    if (!notNullOrUndefined(value)) {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    } else if (typeof value != 'string' && typeof value != 'number') {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    } else if (!this.pattern.test(value)) {
      throw new Error(JSON.stringify({ code: this.code, message: this.message }))
    }
  }
}

export function notNullOrUndefined(value) {
    return value !== null && typeof value !== 'undefined'
}