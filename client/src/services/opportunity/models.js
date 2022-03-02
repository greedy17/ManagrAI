import Model, { fields } from '@thinknimble/tn-models'
import OpportunityAPI from './api'

export default class Opportunity extends Model {
    static api = new OpportunityAPI(Opportunity)
    static id = new fields.IdField({ readOnly: true })
    static integration_source = new fields.CharField({})
    static name = new fields.CharField({})
    static amount = new fields.CharField({})
    static close_date = new fields.IntegerField({})
    static forecast_category = new fields.CharField({})
    static account = new fields.CharField({})
    static account_ref = new fields.CharField({})
    static stage = new fields.Field({})
    static owner = new fields.Field({})
    static owner_ref = new fields.CharField({})
    static last_stage_update = new fields.Field({})
    static last_activity_date = new fields.Field({})
    static external_account = new fields.Field({})
    static external_owner = new fields.Field({})
    static imported_by = new fields.Field({})
    static contacts = new fields.Field({})
    static is_stale = new fields.Field({})
    static secondary_data = new fields.Field({})
}