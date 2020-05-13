import Utils from '@/services/utils'

export class FormControl {
  // optional value that is set based on the value if it is provided otherwise it is blank
  // used for reset
  blankValue = this.value
  constructor({ name = '', validators = [], errors = [], value = '', placeholder = '' } = {}) {
    Object.assign(this, { name, validators, errors, value, placeholder })
  }
  static create(data = {}) {
    return new FormControl(data)
  }
  validate() {
    this.errors = []
    this.errors = this.validators.map(val => {
      return val(this)
    })
    // TODO: Check why it returns duplicate values
    if (this.errors.length > 0) {
      this.errors = Utils.removeDuplicates(this.errors[0])
    }

    return this.errors
  }

  get valid() {
    return this.errors.length > 0 ? false : true
  }
  get errorGetter() {
    return this.errors
  }
  set errorSetter(error) {
    // used to set errors possibly from the server
    // must be in the form {'name':'',message:''}
    // name is the name of the error
    this.errors.push(error)
  }
  set addValidator(validator) {
    this.validators = [...this.validators, validator]
  }
  get Value() {
    return this.value
  }
}

export class FormGroup {
  errors = []
  constructor({ name = '', fields = [], validators = [] } = {}) {
    Object.assign(this, {
      name,
      fields: fields.map((f, i) => {
        // if an array is sent create make it into a form group with name of formArray + the index at current iteration
        if (Array.isArray(f)) {
          f = { fields: [...f], name: 'formArray' + i }
        }
        // instance of a FormArray
        // Form arrays are new form groups
        if (f.hasOwnProperty('fields')) {
          return new FormGroup(f)
        }
        return new FormControl(f)
      }),
      validators,
    })
  }
  static create(data = {}) {
    return new FormGroup(data)
  }

  addFcValidator(field, validator) {
    field.addValidator = validator
  }
  validate() {
    this.errors = []
    // checking field level validators
    this.errors = this.fcs.filter(f => {
      f.validate()
      return f.errorGetter.length > 0
    })
    // checking form level validators
    this.validators.forEach(v => v(this))
  }
  resetForm() {
    this.fcs.forEach(f => (f.value = f.blankValue))
  }

  get fcs() {
    // gets all form fields as an array
    return this.fields
  }

  get fc() {
    // returns all form fields as an object for easier access from the component
    // if a field is a simple array then give it a key of formArray+ its index
    // if a name is provided it becomes a form group and has the name of the form group
    // it is returned as a new instance with its own fc getter

    let formControls = {}
    this.fields.forEach(f => (formControls[f.name] = f))
    return formControls
  }

  get valid() {
    return this.errors.length > 0 ? false : true
  }

  get errorGetter() {
    return this.errors
  }
  get Value() {
    // needs to be updated to get nested form control values as well
    return this.fcs.reduce((acc, curr) => {
      if (acc) {
        acc = { ...acc, [curr.name]: curr.Value }
        return acc
      }
      acc = {}
      return acc
    }, {})
  }
  get Pristine() {
    // future development to see if form field is touched, pristine, dirty
    return this.fcs.map(f => {
      if (f.hasOwnProperty('fields')) {
        return f.fcs.map(f2 => {
          return {
            [f2.name]: f2.Value.length > 0,
          }
        })
      }
      return {
        [f.name]: f.Value.length > 0,
      }
    })
  }
}
