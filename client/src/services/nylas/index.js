import { apiClient, apiErrorHandler } from '@/services/api'

const THREADS_ENDPOINT = '/users/threads/?limit=10'
const MESSAGES_ENDPOINT = '/users/thread-messages/'

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
}
