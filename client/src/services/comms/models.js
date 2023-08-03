import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import CommsApi from './api'

export default class Comms extends Model {
    static api = CommsApi.create(Comms)
    static id = new fields.CharField({ readOnly: true })
}
