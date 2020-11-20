import { objectToCamelCase } from '@/services/utils'
import store from '@/store'
import SlackAPI from './api'

/* 
  If the OAuth request was accepted, the URL will contain a temporary code in a GET code parameter.
  If the OAuth request was denied, the URL will contain a GET error parameter.
  In either case, the URL will also contain the state provided in the initial redirect step in a state parameter.
*/
export default class SlackOAuth {
  static api = SlackAPI.create(SlackOAuth)
  static options = {
    WORKSPACE: 'WORKSPACE',
    USER: 'USER',
  }
  static redirectURI =
    window.location.protocol + '//' + window.location.host + '/settings/slack-integration/callback'

  /*
   * STEP 2: For use in _SlackCallback.vue
   */

  // If the states don't match, the request has been created by a third party and the process should be aborted.

  // NOTE: getAccessToken() works for both workspace and user OAuth.
  // https://api.slack.com/methods/oauth.v2.access
  // getAccessToken = () => {
  //   // Exchange the params.code for an access token using Slack's oauth.access method.
  //   const endpoint = 'https://slack.com/api/oauth.v2.access'
  //   const payload = {
  //     code: this.params.code,
  //     client_id: this.clientID,
  //     client_secret: this.clientSecret,
  //     redirect_uri: this.redirectURI,
  //   }
  //   const config = {
  //     method: 'POST',
  //     Accept: 'application/json',
  //     'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
  //     body: new URLSearchParams(payload),
  //   }
  //   return fetch(endpoint, config)
  //     .then(r => r.json())
  //     .then(json => objectToCamelCase(json))
  // }
}
