import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'
import { objectToCamelCase, objectToSnakeCase, toSnakeCase } from '@thinknimble/tn-utils'
import moment from 'moment'
const POLLING_COUNT_ENDPOINT = 'polling/count'

export default {
  async listPollingCount(items, lastCheckedAt = moment()) {
    const url = POLLING_COUNT_ENDPOINT
    const client = apiClient()

    const data = { items: items, last_checked_at: lastCheckedAt }
    const res = await client.post(url, data)

    let d = objectToCamelCase(res.data)

    return d
  },
}
