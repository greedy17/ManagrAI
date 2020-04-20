import store from '@/store'

export default {
  getHeaders,
}

function getHeaders() {
  if (!store.state.token) {
    return {}
  }
  return {
    Authorization: `Token ${store.state.token}`,
  }
}

//  NOTE(Bruno 4-8-20): login/logout functionality is within the UserAPI.
