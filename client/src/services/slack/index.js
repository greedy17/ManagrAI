import { urlQueryParams, objectToCamelCase } from '@/services/utils'
import store from '@/store'

const WORKSPACE_SCOPES = [
  'app_mentions:read',
  'channels:join',
  'channels:read',
  'chat:write',
  'chat:write.public',
  'commands',
  'im:history',
  'im:write',
  'incoming-webhook',
  'links:read',
  'links:write',
  'mpim:history',
  'mpim:read',
  'mpim:write',
  'team:read',
  'users:read',
  'users:read.email',
]

const USER_SCOPES = ['identity.basic']

/* 
  If the OAuth request was accepted, the URL will contain a temporary code in a GET code parameter.
  If the OAuth request was denied, the URL will contain a GET error parameter.
  In either case, the URL will also contain the state provided in the initial redirect step in a state parameter.
*/
export default class SlackOAuth {
  constructor() {
    this.params = urlQueryParams()
    this.userID = store.state.user.id
  }

  get clientID() {
    return process.env.VUE_APP_SLACK_CLIENT_ID
  }

  get clientSecret() {
    return process.env.VUE_APP_SLACK_CLIENT_SECRET
  }

  get redirectURI() {
    return (
      window.location.protocol +
      '//' +
      window.location.host +
      '/settings/slack-integration/callback'
    )
  }

  get slackRootURI() {
    return 'https://slack.com/oauth/v2/authorize'
  }

  // parameters:
  get workspaceScopesParam() {
    return 'scope=' + WORKSPACE_SCOPES.join(',')
  }

  get userScopesParam() {
    return 'user_scope=' + USER_SCOPES.join(',')
  }

  get clientIdParam() {
    return 'client_id=' + this.clientID
  }

  get redirectUriParam() {
    return 'redirect_uri=' + this.redirectURI
  }

  get stateParam() {
    return 'state=' + this.userID
  }

  /*
   * STEP 1: For use in SlacIntegration.vue
   */

  get addToWorkspaceLink() {
    let params = [
      this.workspaceScopesParam,
      this.clientIdParam,
      this.stateParam,
      this.redirectUriParam,
    ]
    return this.slackRootURI + '?' + params.join('&')
  }

  //TODO: add teamParam and add it to userSignIn

  get userSignInLink() {
    let params = [this.userScopesParam, this.clientIdParam, this.stateParam, this.redirectUriParam]
    return this.slackRootURI + '?' + params.join('&')
  }

  /*
   * STEP 2: For use in _SlackCallback.vue
   */

  // If the states don't match, the request has been created by a third party and the process should be aborted.
  get stateParamIsValid() {
    return this.params.state === this.userID
  }

  // NOTE: getAccessToken() works for both workspace and user OAuth.
  // https://api.slack.com/methods/oauth.v2.access
  getAccessToken = () => {
    // Exchange the params.code for an access token using Slack's oauth.access method.
    const endpoint = 'https://slack.com/api/oauth.v2.access'
    const payload = {
      code: this.params.code,
      client_id: this.clientID,
      client_secret: this.clientSecret,
      redirect_uri: this.redirectURI,
    }
    const config = {
      method: 'POST',
      Accept: 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      body: new URLSearchParams(payload),
    }
    return fetch(endpoint, config)
      .then(r => r.json())
      .then(json => objectToCamelCase(json))
  }
}
