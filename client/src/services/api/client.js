import axios from 'axios'
import CSRF from '@/services/csrf'
import Auth from '@/services/auth'
import API_BASE from './base'

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
  return axios.create({
    baseURL: `${location.protocol}//${location.host}` + API_BASE,
    headers: {
      ...CSRF.getHeaders(),
      ...Auth.getHeaders(),
    },
  })
}
