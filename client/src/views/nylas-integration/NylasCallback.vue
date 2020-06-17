<template>
  <div></div>
</template>

<script>
/**
 * This component receives the callback from the Nylas OAuth flow.
 * 
 * It looks for the 'code' and 'state' query parameters and passes those
 * to the back end, which retrieves an access token for the user and
 * finalizes the OAuth flow.
 * 
 * This component doesn't have any visible elements except for an Alert
 * box. Whether success or failure, the page generates an alert and
 * redirects back to the settings page.
 */
import Nylas from '@/services/nylas'

export default {
  name: 'NylasCallback',
  data() {
    return {
    }
  },
  created() {
    const magicToken = this.$route.query.state
    const code = this.$route.query.code

    Nylas.retrieveUserToken(code, magicToken)
        .then(() => {
            this.$Alert.alert({
                type: 'success',
                message: `
                    <h3>Success</h3>
                    <p>Your account is now connected to your email.</p>
                `,
            })
        })
        .catch((error) => {
            this.$Alert.alert({
                type: 'error',
                message: `
                    <h3>Error</h3>
                    <p>Could not complete the email connection. The error message is:</p>
                    <p>${error}</p>
                `,
            })
        })
        .finally(() => {
            this.$router.replace({ name: 'Settings' })
            this.$store.dispatch('refreshCurrentUser')
        })
  },
}
</script>

<style lang="scss" scoped></style>
