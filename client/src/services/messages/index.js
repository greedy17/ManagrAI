import { apiClient, apiErrorHandler, ApiFilter } from '@/services/api'
const SEND_MESSAGE_URI = 'users/send-text-message/'
export default {
  async sendMessage(body, recipients) {
    const url = SEND_MESSAGE_URI
    const client = apiClient()
    const data = { body: body, recipients: recipients }
    await client.post(url, data)
  },
}
