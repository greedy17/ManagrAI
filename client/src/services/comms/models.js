import Model, { fields } from '@thinknimble/tn-models'
import { CommsApi, TwitterAccountAPI } from './api'

class Comms extends Model {
    static api = CommsApi.create(Comms)
    static id = new fields.CharField({ readOnly: true })
}

class Twitter extends Model {
    static api = TwitterAccountAPI.create(Twitter)
}

export { Comms, Twitter }