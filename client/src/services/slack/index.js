import SlackAPI from './api'

export default class SlackOAuth {
  static api = SlackAPI.create(SlackOAuth)
  static options = {
    WORKSPACE: 'WORKSPACE',
    USER: 'USER',
  }
  static redirectURI =
    window.location.protocol + '//' + window.location.host + '/settings/integrations'
}
