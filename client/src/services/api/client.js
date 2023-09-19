import axios from 'axios'
import CSRF from '@/services/csrf'
import Auth from '@/services/auth'
import API_BASE from './base'
import store from '../../store'
import User from '../users'
import router from '../../router'

/**
 *   Get the axios API client.
 *   This conveniently sets the `baseURL` and `headers` for the API client,
 *   so that we don't have to do this in every function that needs to call
 *   the API.
 *
 *   @returns {object} - An instance of the axios API client.
 */
export function apiClient() {
  const { location } = window
  const instance = axios.create({
    baseURL: `${location.protocol}//${location.host}` + API_BASE,
    headers: {
      ...CSRF.getHeaders(),
      ...Auth.getHeaders(),
    },
  })
  instance.interceptors.response.use(
    (response) => {
      // Successful responses are passed through
      return response;
    },
    (error) => {
      // console.log('hi error', error.response, error.response.status === 401, error.response.data.detail === 'Token expired')
      if (error.response.status === 401 && error.response.data.detail === 'Token expired') {
        // Handle the 401 Unauthorized error here
        // For example, you can log the user out or show an error message
        // You can also redirect the user to the login page
        // let tempUser
        // if (store.getters.user && store.getters.user.id) {
        //   store.dispatch('updateTempRefreshUser', store.getters.user)
        //   tempUser = store.getters.user
        // } else {
        //   tempUser = store.getters.tempRefreshUser
        // }
        // const user = store.getters.user
        // const token = store.getters.token
        // console.log('user', user)
        // console.log('token', token)
        // call refresh token endpoint
        // User.api.refreshToken(token, user && user.id ? user.id : tempUser.id).then((res) => {
        //   // with token, insert into store
        //   console.log('res', res)
        //   store.dispatch('updateUserToken', res.token).then(() => {
        //     store.dispatch('updateUser', tempUser).then(() => {
        //       // refresh user
        //       // store.dispatch('refreshCurrentUser').then(() => {
        //       //   store.dispatch('updateTempRefreshUser', null)
        //       //   // router.go()
        //       // })
        //     })
        //   })
        // })
        return Promise.reject(error);
      } else {
        return Promise.reject(error);
      }
    }
  );
  return instance
}
