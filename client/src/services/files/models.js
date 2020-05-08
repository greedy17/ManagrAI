import { objectToCamelCase, objectToSnakeCase } from '@/services/utils'
import FileAPI from './api'

export default class File {
  static api = FileAPI.create(File)

  //   constructor({ id = '' } = {}) {
  //     Object.assign(this, {
  //       id,
  //     })
  //   }
  constructor(file) {
    console.log('file', file)
  }
  static create(opts) {
    return new File(opts)
  }

  static fromAPI(json) {
    return new File(objectToCamelCase(json))
  }

  static toAPI(json) {
    const data = objectToSnakeCase(json)
    return data
  }

  clone() {
    return new File(this)
  }
}
