<template>
  <div class="zoom-page">
    <template v-if="!user.zoomAccount">
      <div>
        Please Integrate You're Zoom Account
      </div>
    </template>
    <template v-else>
      <TestMeetings v-if="devOrStaging" />
    </template>
  </div>
</template>

<script>
/**
 *
 * This page contains meetings from zoom
 * Meetings that have been saved for a user
 * A special section for dev and staging to test against
 *
 */
import TestMeetings from '@/views/zoom/_TestMeetings'
export default {
  name: 'ZoomPage',
  components: { TestMeetings },
  computed: {
    user() {
      return this.$store.state.user
    },
    devOrStaging() {
      return process.env.NODE_ENV == 'development' || process.env.NODE_ENV == 'staging'
    },
  },
}
</script>

<style lang="scss" scoped></style>
