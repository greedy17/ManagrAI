<template>
  <div></div>
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
import SlackOAuth from '@/services/slack'

export default {
  name: 'SlackCallback',
  async created() {
    const { state, error, code } = this.$route.query
    // If the states don't match, the request has been created by a third party and the process should be aborted.
    let invalidStateParam = state !== this.$store.state.user.id
    if (invalidStateParam || error) {
      this.$Alert.alert({
        type: 'error',
        timeout: 3000,
        message: 'Could not integrate Slack.',
      })
      this.$router.push({ name: 'SlackIntegration' })
      return
    }
    // Ask our server to exchange the params.code for an access token.
    SlackOAuth.api
      .generateAccessToken(code)
      .then(updatedUser => {
        this.$store.dispatch('updateUser', updatedUser)
        SlackOAuth.api.testDM()
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Slack integration successful.',
        })
      })
      .finally(() => {
        // Take user back to Settings page.
        this.$router.push({ name: 'SlackIntegration' })
      })
  },
}
</script>

<style lang="scss" scoped></style>
