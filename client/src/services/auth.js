import store from '@/vuex/store';

export default {
  getHeaders() {
    if (!store.state.authToken) {
      return {};
    }
    return {
      Authorization: `Token ${store.state.authToken}`,
    };
  },
};
