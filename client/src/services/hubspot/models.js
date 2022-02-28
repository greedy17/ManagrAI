import Model, { fields } from '@thinknimble/tn-models'
import { objectToCamelCase, objectToSnakeCase } from '@thinknimble/tn-utils'

import HubspotAPI from './api'

export default class Hubspot extends Model {
    static api = HubspotAPI.create(Hubspot)
    static id = new fields.CharField({ readOnly: true })

    static fromAPI(json) {
        return new Hubspot(objectToCamelCase(json))
    }

    static toAPI(json, fields = [], excludedFields = []) {
        return objectToSnakeCase(json)
    }
}
