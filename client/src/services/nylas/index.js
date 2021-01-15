import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'
import { objectToCamelCase } from '@thinknimble/tn-utils'

const REVOKE_TOKEN_ENDPOINT = '/users/revoke-email-auth/'
const RETRIEVE_TOKEN_ENDPOINT = '/users/nylas/authenticate/'
const ATTACH_FILE_ENDPOINT = '/users/attach-file/'
const DOWNLOAD_FILE_ENDPOINT = id => `/get-file/${id}/`

export default {
  downloadFile(fileId) {
    const params = {
      responseType: 'blob',
    }
    const promise = apiClient()
      .get(DOWNLOAD_FILE_ENDPOINT(fileId), params)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.downloadFile' }))
    return promise
  },
  attachFile(file) {
    const headers = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
    var fileFormData = new FormData()
    fileFormData.append('file', file)
    const promise = apiClient()
      .post(ATTACH_FILE_ENDPOINT, fileFormData, headers)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.attachFile' }))
    return promise
  },
  api: {
    authenticate(code) {
      const data = { code }
      return apiClient()
        .post(RETRIEVE_TOKEN_ENDPOINT, data)
        .then(res => objectToCamelCase(res.data))
        .catch(apiErrorHandler({ apiName: 'NylasAPI.retrieveToken' }))
    },
    getAuthLink() {
      return apiClient()
        .get('/users/nylas/authorization/')
        .then(res => objectToCamelCase(res.data))
        .catch(apiErrorHandler({ apiName: 'NylasAPI.retrieveToken' }))
    },
    revokeUserToken() {
      const promise = apiClient()
        .post(REVOKE_TOKEN_ENDPOINT)
        .catch(apiErrorHandler({ apiName: 'NylasAPI.revokeToken' }))
      return promise
    },
  },
}
