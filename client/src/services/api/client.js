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
 *   @param {AbortController} abortController - An instance of AbortController for request cancellation.
 *   @returns {object} - An instance of the axios API client.
 */
export function apiClient(abortController = { signal: null }) {
  const { location } = window
  const instance = axios.create({
    baseURL: `${location.protocol}//${location.host}` + API_BASE,
    headers: {
      ...CSRF.getHeaders(),
      ...Auth.getHeaders(),
    },
    signal: abortController.signal,
  })
  instance.defaults.signal = abortController.signal
  instance.interceptors.response.use(
    (response) => {
      // Successful responses are passed through
      return response;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  return instance
}
