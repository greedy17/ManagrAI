import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'

export default class ZoomMeetingAPI extends ModelAPI {
  static ENDPOINT = 'users/zoom/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }
}
