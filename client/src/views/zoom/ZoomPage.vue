<template>
  <div class="zoom-page">
    <div class="zoom-page__main-content-area">
      <template v-if="!user.zoomAccount">
        <div>
          Please Integrate You're Zoom Account
        </div>
      </template>
      <template v-else>
        <div class="zoom-page__main-content-area__items">
          <div class="zoom-page__main-content-area__items__item"></div>
          <div class="zoom-page__main-content-area__items__item">
            <TrackedMeetings />
          </div>
          <div class="zoom-page__main-content-area__items__item">
            <TestMeetings v-if="devOrStaging" />
          </div>
        </div>
      </template>
    </div>
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
import TrackedMeetings from '@/views/zoom/_TrackedMeetings'
export default {
  name: 'ZoomPage',
  components: { TestMeetings, TrackedMeetings },
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

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
.zoom-page {
  @include page();
  &__main-content-area {
    //most styles inherited from page mixin
    // additional styles included here
  }
}
</style>
