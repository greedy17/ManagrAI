<template>
  <div class="test-meeting-wrapper">
    <div class="test-meeting-wrapper__content">
      <span @click="onCreateMeeting" class="test-meeting-wrapper__content-create">
        Create Meeting
      </span>
      <br />
      <span v-if="meeting" class="test-meeting-wrapper__content-meeting">
        <a :href="meeting.start_url" target="_blank">Start Meeting</a>
        <br />
        password: {{ meeting.password }}
      </span>
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
    }
  },
  methods: {
    async onCreateMeeting() {
      this.meeting = await this.createMeeting()
    },
    async createMeeting() {
      try {
        const res = await ZoomAccount.api.createMeeting()
        return res
      } catch {
        console.log('An error occurred')
      }
    },
  },
}
</script>

<style lang="scss" scoped></style>
