import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'

const THREADS_ENDPOINT = '/users/threads/'
const MESSAGES_ENDPOINT = '/users/thread-messages/'
const SEND_EMAIL_ENDPOINT = '/users/send-email/'
const PREVIEW_EMAIL_ENDPOINT = '/users/preview-email/'
const REVOKE_TOKEN_ENDPOINT = '/users/revoke-email-auth/'
const RETRIEVE_TOKEN_ENDPOINT = '/users/email-auth-token/'
const ATTACH_FILE_ENDPOINT = '/users/attach-file/'
const DOWNLOAD_FILE_ENDPOINT = id => `/get-file/${id}/`

export default {
  getThreads({ filters, enable400Alert, enable500Alert, rethrowErrors } = {}) {
    const filtersMap = {
      page: ApiFilter.create({ key: 'page' }),
      pageSize: ApiFilter.create({ key: 'page_size' }),
      toEmail: ApiFilter.create({ key: 'to_email' }),
      anyEmail: ApiFilter.create({ key: 'any_email' }),
    }
    const options = {
      params: ApiFilter.buildParams(filtersMap, { ...filters }),
    }

    const promise = apiClient()
      .get(THREADS_ENDPOINT, options)
      .then(response => response.data)
      .catch(
        apiErrorHandler({
          apiName: 'NylasAPI.getThreads',
          enable400Alert,
          enable500Alert,
          rethrowErrors,
        }),
      )
    return promise
  },
  getThreadMessages(threadId) {
    const data = {
      threadId,
    }
    const promise = apiClient()
      .post(MESSAGES_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.getThreadMessages' }))
    return promise
  },
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
  sendEmail({
    to,
    subject,
    body,
    lead,
    ccEmails = [],
    bccEmails = [],
    replyMessageId = '',
    fileIds = [],
    variables = {},
  }) {
    /*
    Use Nylas to send emails from this user.
    PARAMS:
      subject: A string for the subject of the email.
      body: A string for the body of the email.
      recipient_email: An array of contact objects for the To field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.
      cc_email: An array of contact objects for the CC field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.
      bcc_email: An array of contact objects for the BCC field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.

      NOTE: WE NEED TO MAKE SURE THESE TWO FUNCTIONS, PREVIEWEMAIL AND SENDEMAIL, STAY IN SYNC.
      TODO: FIND A WAY TO COMBINE THEM.
    */

    const data = {
      subject,
      body,
      lead,
      to,
      cc: ccEmails,
      bcc: bccEmails,
      reply_to_message_id: replyMessageId,
      file_ids: fileIds,
      variables: variables,
    }
    const promise = apiClient()
      .post(SEND_EMAIL_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.sendEmail' }))
    return promise
  },
  previewEmail({
    to,
    subject,
    body,
    lead,
    ccEmails = [],
    bccEmails = [],
    replyMessageId = '',
    fileIds = [],
    variables = {},
  }) {
    /*
    Use Nylas to preview emails from this user.
    PARAMS:
      subject: A string for the subject of the email.
      body: A string for the body of the email.
      recipient_email: An array of contact objects for the To field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.
      cc_email: An array of contact objects for the CC field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.
      bcc_email: An array of contact objects for the BCC field.
            Contact objects must be in the format { "name": NAME, "email": EMAIL }.

      NOTE: WE NEED TO MAKE SURE THESE TWO FUNCTIONS, PREVIEWEMAIL AND SENDEMAIL, STAY IN SYNC.
      TODO: FIND A WAY TO COMBINE THEM.
    */

    const data = {
      subject,
      body,
      to,
      lead,
      cc: ccEmails,
      bcc: bccEmails,
      reply_to_message_id: replyMessageId,
      file_ids: fileIds,
      variables: variables,
    }
    const promise = apiClient()
      .post(PREVIEW_EMAIL_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.previewEmail' }))
    return promise
  },
  retrieveUserToken(code, magicToken) {
    const data = { code, magic_token: magicToken }
    return apiClient()
      .post(RETRIEVE_TOKEN_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.retrieveToken' }))
  },
  revokeUserToken() {
    const promise = apiClient()
      .post(REVOKE_TOKEN_ENDPOINT)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.revokeToken' }))
    return promise
  },
}
