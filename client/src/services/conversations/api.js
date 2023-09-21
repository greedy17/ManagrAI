import { apiClient, apiErrorHandler, ApiFilter } from '../api'

export default class ConversationsAPI {
    get client() {
      return apiClient()
    }
  
    /**
     * Instantiate a new `ConversationsAPI`
     *
     * @param {class} cls - The class to use to create objects.
     */
    constructor(cls) {
      this.cls = cls
    }
  
    /**
     * Factory method to create a new instance of `ConversationsAPI`.
     *
     * @param {class} cls - The class to use to create objects.
     **/
    static create(cls) {
      return new ConversationsAPI(cls)
    }
  
    async list({ pagination, filters }) {
      const url = 'conversations/'
      try {
        const res = await this.client.get(url)
        return {
          ...res.data,
        }
      } catch (e) {
        console.log('Error in list/conversations', e)
        // apiErrorHandler({ apiName: 'UsersAPI.list' })
      }
    }

    // This function will not be necessary if messages are contained in the conversations list
    // async listMessages(id) {
    //   const url = `conversations/${id}/`
    //   try {
    //     const res = await this.client.get(url)
    //     return {
    //       ...res.data,
    //     }
    //   } catch (e) {
    //     console.log('Error in list/conversations', e)
    //     // apiErrorHandler({ apiName: 'UsersAPI.list' })
    //   }
    // }

    async sendMessage(id, data) {
      try {
        console.log('sent message', data)
        // const res = await this.client.post(`conversations/${id}/`, { data })
        // return res.data
      } catch (e) {
        console.log('Error in sendMessage/conversations', e)
        // apiErrorHandler({ apiName: 'Error Retrieving Data' })(e)
      }
    }
        
    async editMessage(id, data) {
      const d = objectToSnakeCase(data)
      try {
        await this.client.patch(`conversations/${id}/`, d)
      } catch (e) {
        console.log('Error in editMessage/conversations', e)
        // apiErrorHandler({ apiName: 'AlertTemplateAPI.UpdateAlertTemplate' })(e)
      }
    }
}