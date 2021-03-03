<template>
  <div class="test-meeting-subpage">
    <div class="test-meeting-subpage__header">
      <div class="test-meeting-subpage__title">
        Begin Meeting Interaction
      </div>
    </div>

    <div class="test-meeting-subpage__content">
      <span @click="onKickOff" class="test-meeting-subpage__content-create">
        Kick Off Slack Interaction with Zoom Meeting
      </span>
      <br />
      <span v-if="interactionInProgress" class="test-meeting-subpage__content-meeting">
        This Zoom Meeting has two participants:
        <br />
        pb1646a@gmail.com is a participant that exists as a contact to a selected opportunity
        <br />
        bakerpari@yahoo.com is a participant that does not exist in our current contacts list this
        participant will be added as part of the meeting data
        <br />
        If a different opportunity is selected both these contacts will appear as linked contacts
        for that opporunity
      </span>
      <br />
      <button v-if="interactionInProgress" :disabled="loading" @click="onGenerateScore">
        Generate Score
      </button>
      <button v-if="interactionInProgress" :disabled="loading" @click="reset">
        Clear Data to Try again
      </button>
    </div>
  </div>
</template>

<script>
/**
 *
 * A special section for dev and staging to test against
 *
 */
import ZoomAccount from '@/services/zoom/account/'
export default {
  name: 'TestMeetings',
  data() {
    return {
      meeting: null,
      interactionInProgress: false,
      loading: false,
    }
  },
  methods: {
    timeblocker() {
      this.loading = true

      setTimeout(() => {
        this.loading = false
      }, 8000)
    },
    async onGenerateScore() {
      await ZoomAccount.api.demoGenerateScore()
      this.timeblocker()
    },
    async onKickOff() {
      await ZoomAccount.api.clearDemoMeeting()
      this.interactionInProgress = true
      await ZoomAccount.api.fakeMeetingEnd()
      this.timeblocker()
    },
    async reset() {
      await ZoomAccount.api.clearDemoMeeting()
      this.interactionInProgress = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
.test-meeting-subpage {
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
