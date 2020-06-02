import { apiClient, apiErrorHandler } from '@/services/api'

const THREADS_ENDPOINT = '/users/threads/'
const MESSAGES_ENDPOINT = '/users/thread-messages/'
const SEND_EMAIL_ENDPOINT = '/users/send-email/'
const PREVIEW_EMAIL_ENDPOINT = '/users/preview-email/'
const REVOKE_TOKEN_ENDPOINT = '/users/revoke-email-auth/'

export default {
  getUserThreads(toEmail = null) {
    const data = {
      to_email: toEmail,
    }
    const promise = apiClient()
      .post(THREADS_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.getUserThreads' }))
    return promise
  },
  getThreadMessages(threadId) {
    const data = {
      threadId,
    }
    const promise = apiClient()
      .post(MESSAGES_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.getUserThreads' }))
    return promise
  },
  sendEmail(to, subject, body, ccEmails = [], bccEmails = [], replyMessageId = '', variables = {}) {
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
      to,
      cc: ccEmails,
      bcc: bccEmails,
      reply_to_message_id: replyMessageId,
      variables: variables,
    }
    const promise = apiClient()
      .post(SEND_EMAIL_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.sendEmail' }))
    return promise
  },
  previewEmail(
    to,
    subject,
    body,
    ccEmails = [],
    bccEmails = [],
    replyMessageId = '',
    variables = {},
  ) {
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
      cc: ccEmails,
      bcc: bccEmails,
      reply_to_message_id: replyMessageId,
      variables: variables,
    }
    const promise = apiClient()
      .post(PREVIEW_EMAIL_ENDPOINT, data)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.previewEmail' }))
    return promise
  },
  revokeUserToken() {
    const promise = apiClient()
      .post(REVOKE_TOKEN_ENDPOINT)
      .catch(apiErrorHandler({ apiName: 'NylasAPI.revokeToken' }))
    return promise
  },
}
