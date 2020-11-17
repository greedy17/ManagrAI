<template>
  <div>callback</div>
</template>

<script>
/**
 * This component receives the callback from the Slack OAuth flow.
 *
 * If the OAuth request was accepted, the URL will contain a temporary code in a GET code parameter.
 * If the OAuth request was denied, the URL will contain a GET error parameter.
 * In either case, the URL will also contain the state provided in the initial redirect step in a state parameter.
 *
 * This component doesn't have any visible elements except for an Alert
 * box. Whether success or failure, the page generates an alert and
 * redirects back to the settings page.
 */
import SlackOAuthModel from '@/services/slack'

export default {
  name: 'SlackCallback',
  created() {
    let slackOAuth = new SlackOAuthModel()
    // If the states don't match, the request has been created by a third party and the process should be aborted.
    if (!slackOAuth.stateParamIsValid) {
      return
    }
    if (slackOAuth.params.error) {
      this.$Alert.alert({
        type: 'error',
        timeout: 3000,
        message: 'Could not integrate Slack.',
      })
      this.$router.push({ name: 'SlackIntegration' })
      return
    }
    // Now will need to exchange the params.code for an access token using the oauth.access method.
    // https://api.slack.com/methods/oauth.v2.access
    slackOAuth.getAccessToken().then(data => {
      debugger
    })
  },
}
</script>

<style lang="scss" scoped></style>
