import { urlQueryParams } from '@/services/utils'
import store from '@/store'

const workspaceScopes = [
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

/* 
  If the OAuth request was accepted, the URL will contain a temporary code in a GET code parameter.
  If the OAuth request was denied, the URL will contain a GET error parameter.
  In either case, the URL will also contain the state provided in the initial redirect step in a state parameter.
*/
export default class SlackOAuth {
  static workspaceScopes = workspaceScopes

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
    return window.location.protocol + '//' + window.location.host + '/settings'
  }

  get workspaceScopesParams() {
    return SlackOAuth.workspaceScopes.join(',')
  }

  get workspaceOptionalParams() {
    // Can specify the following three optional parameters:
    // redirect_uri -- The URL to redirect back to upon authorization
    // state -- unique string to be passed back upon completion
    // team -- Slack team ID of the authenticated user to the integration or app to that team
    const params = {
      redirect_uri: this.redirectURI,
      state: this.userID,
      //   team: ?
    }
    return `redirect_uri=${params.redirect_uri}&state=${params.state}`
  }

  get addToWorkspaceLink() {
    return `https://slack.com/oauth/v2/authorize?scope=${this.workspaceScopesParams}&client_id=${this.clientID}&${this.workspaceOptionalParams}`
  }

  get userSignInLink() {
    return `https://slack.com/oauth/v2/authorize?user_scope=identity.basic&client_id=${this.clientID}`
  }

  // STEP 2:

  get isSlackOAuthRedirect() {
    return !!((this.params.code || this.params.error) && this.params.state)
  }

  // If the states don't match, the request has been created by a third party and the process should be aborted.
  get stateParamIsValid() {
    return this.params.state === this.userID
  }

  getAccessToken = () => {
    // Exchange the params.code for an access token using Slack's oauth.access method.
    // https://api.slack.com/methods/oauth.v2.access
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
    return fetch(endpoint, config).then(r => r.json())
  }
}
