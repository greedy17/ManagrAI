<template>
  <div class="tracked-meetings-subpage">
    <div class="tracked-meetings-subpage__header">
      <div class="tracked-meetings-subpage__title">
        Tracked Meetings
      </div>
    </div>
    <div class="tracked-meetings-subpage__content"></div>
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
import ZoomMeeting from '@/services/zoommeetings'
import CollectionManager from '@thinknimble/tn-models'
export default {
  name: 'TrackedMeetings',
  components: {},
  data() {
    return {
      meetings: CollectionManager.create({
        ModelClass: ZoomMeeting,
        filters: {},
      }),
    }
  },
  created() {
    console.log(ZoomMeeting)
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
.tracked-meetings-subpage {
  @include box--bordered();
  &__content {
    &-create {
      &:hover {
        cursor: pointer;
      }
    }
  }
}
</style>
