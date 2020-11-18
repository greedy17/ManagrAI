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
import SlackOAuthModel from '@/services/slack'
import Organization from '@/services/organizations'
import User from '@/services/users'

export default {
  name: 'SlackCallback',
  async created() {
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
    // Exchange the params.code for an access token.
    await slackOAuth.getAccessToken().then(this.handleAccessToken)
    // Take user back to Settings page.
    this.$router.push({ name: 'SlackIntegration' })
  },
  methods: {
    async handleAccessToken(data) {
      /*
       NOTE:
       Only AddToWorkspace yields tokenType == 'bot'.
       Both AddToWorkspace and UserSignIn yield data.authedUser, and in both cases
       the user needs to integrate slack.
       Therefore User.integrateSlack can and should take place regardless.
      */

      // STEP 1: if addToWorkspace, integrateSlack at Organization-level
      if (data.tokenType === 'bot') {
        let {
          scope,
          team: { name: teamName, id: teamId },
          botUserId,
          accessToken,
          incomingWebhook,
          enterprise,
        } = data

        let payload = {
          scope,
          teamName,
          teamId,
          botUserId,
          accessToken,
          incomingWebhook,
          enterprise,
        }

        await Organization.api
          .integrateSlack(this.$store.state.user.organizationRef.id, payload)
          .then(organization => {
            // update store state with user's updated orgRef (has org.slackRef)
            let user = { ...this.$store.state.user }
            user.organizationRef = organization
            return this.$store.dispatch('updateUser', user)
          })
      }

      // STEP 2: integrate slack at the user-level
      let {
        team: { id: teamId },
        authedUser: { id: slackId },
      } = data
      // check to see if user selected proper workspace to sign into.
      // abort if invalid workspace
      if (teamId !== this.$store.state.user.organizationRef.slackRef.teamId) {
        this.$Alert.alert({
          type: 'error',
          timeout: 3000,
          message: 'You signed into the wrong Slack workspace, please try again.',
        })
        return
      }
      await User.api.integrateSlack(this.$store.state.user.id, slackId).then(user => {
        // update store state with new user (has user.slackRef)
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Slack integration successful.',
        })
        return this.$store.dispatch('updateUser', user)
      })
    },
  },
}
</script>

<style lang="scss" scoped></style>
