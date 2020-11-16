<template>
  <div class="zoom-integration">
    <button @click="getZoomAuthLink">Get Link</button>

    {{ authLink }}
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
        await ZoomAccount.api.getAuthData(this.$route.query.code)
      } catch (e) {
        console.log(e)
      } finally {
        this.generatingToken = false
      }
    }
  },
  methods: {
    async getZoomAuthLink() {
      const res = await ZoomAccount.api.getAuthLink()
      this.authLink = res
      if (res.link) {
        window.open(res.link)
      }
    },
  },
}
</script>

<style lang="scss" scoped></style>
