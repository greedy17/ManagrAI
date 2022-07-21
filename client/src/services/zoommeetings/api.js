import { apiClient, apiErrorHandler } from '@/services/api'
import { ModelAPI, ApiFilter } from '@thinknimble/tn-models'

const ZOOM_MEETING_ENDPOINT = 'zoom/schedule-zoom-meeting/'

export default class ZoomMeetingAPI extends ModelAPI {
  static ENDPOINT = 'users/zoom/'
  static FILTERS_MAP = {
    page: ApiFilter.create({ key: 'page' }),
    pageSize: ApiFilter.create({ key: 'page_size' }),
  }

  get client() {
    return apiClient()
  }

  /**
   * Instantiate a new `ZoomMeetingAPI`
   *
   * @param {class} cls - The class to use to create objects.
   */
  //  constructor(cls) {
  //   this.cls = cls
  // }

  /**
   * Factory method to create a new instance of `ZoomMeetingAPI`.
   *
   * @param {class} cls - The class to use to create objects.
   **/
  //  static create(cls) {
  //   return new ZoomMeetingAPI(cls)
  // }

  // createZoomMeeting(zoomMeeting) {
  //   // const data = zoomMeeting.toAPI()

  //   console.log('hit?', zoomMeeting)
  //   return this.client
  //     .post(ZOOM_MEETING_ENDPOINT, zoomMeeting)
  //     .then(response => response.data)
  //     .catch(
  //       apiErrorHandler({
  //         apiName: 'Create Zoom Meeting',
  //         enable400Alert: true,
  //         enable500Alert: true,
  //       }),
  //     )
  // }

  async createZoomMeeting(data) {
    try {
      const res = await this.client.post(ZOOM_MEETING_ENDPOINT, { data: data })
      return res.data
    } catch (e) {
      apiErrorHandler({ apiName: 'Error Retrieving Zoom Auth Link' })(e)
    }
  }
}
