<template>
  <div class="zoom-integration">
    <button :disabled="$store.state.user.zoomAccount" @click="getZoomAuthLink">
      Get Link
    </button>
  </div>
</template>

<script>
import ZoomAccount from '@/services/zoom/account/'
export default {
  name: 'ZoomIntegration',
  data() {
    return {
      generatingToken: false,
      authLink: null,
    }
  },
  async created() {
    if (this.$route.query.code) {
      this.generatingToken = true
      // send the code to the backend for processing
      try {
        const res = await ZoomAccount.api.getAuthData(this.$route.query.code)

        if (res) {
          await this.$store.dispatch('refreshCurrentUser')

          this.$router.replace({
            name: 'ZoomIntegration',
            params: {},
          })
        }
      } catch (e) {
        this.$Alert.alert({
          message: 'There was an error validating your token',
          type: 'error',
          timeout: 3000,
        })
      } finally {
        this.generatingToken = false
      }
    }
  },
  methods: {
    async getZoomAuthLink() {
      this.generatingToken = true
      try {
        const res = await ZoomAccount.api.getAuthLink()
        if (res.link) {
          window.location.href = res.link
        }
      } catch (e) {
        console.log(e)
        this.generatingToken = false
        this.$Alert.alert({
          message: 'There was a problem generating your link',
          type: 'error',
          timeout: 3000,
        })
      }
    },
  },
}
</script>

<style lang="scss" scoped></style>
