<template>
  <div class="tracked-meetings-subpage">
    <div class="tracked-meetings-subpage__header">
      <div class="tracked-meetings-subpage__title">
        Trigger Slack Notifications for a lead
      </div>
    </div>
    <div class="tracked-meetings-subpage__content">
      <div class="tracked-meetings-subpage__lead">
        <label>Select a lead to clear data for:</label>
        <select @change="selectLead" v-model="selectedLead">
          <option value="null">Select A Lead</option>
          <option :key="lead.id" v-for="lead in leads.list" :value="lead.id"
            >{{ lead.title }}
          </option></select
        >
      </div>
      <div class="tracked-meetings-subpage__actions">
        <div class="button-group">
          <button @click="stall" :disabled="!selectedLead">Stalled In stage</button>
          <small
            >This will set the lead's stage last update to 60 days in the past and trigger a slack
            alert</small
          >
        </div>
        <div class="button-group">
          <button @click="inactive" :disabled="!selectedLead">Last Activity</button>
          <small>This will clear a lead's activity log trigger a slack alert for inactivity</small>
        </div>
        <div class="button-group">
          <select @change="selectedDays = $event.target.value" v-model="selectedDays">
            <option value="null">Select Days</option>
            <option value="1">1 day</option>
            <option value="2">2 days</option>
            <option value="3">3 days</option>
          </select>
          <button @click="delay" :disabled="!selectedLead || !selectedDays">
            Past Expected Close Date
          </button>
          <small
            >This will set the lead's expected close date to be past the expected close date</small
          >
        </div>
      </div>
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
import ZoomMeeting from '@/services/zoommeetings'
import CollectionManager from '@/services/collectionManager'
import Lead from '@/services/leads'

export default {
  name: 'TrackedMeetings',
  components: {},
  data() {
    return {
      selectedDays: null,
      selectedLead: null,
      meetings: CollectionManager.create({
        ModelClass: ZoomMeeting,
        filters: {},
      }),
      leads: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byReps: [this.$store.state.user.id],
        },
      }),
    }
  },
  async created() {
    await this.leads.refresh()
  },
  methods: {
    selectLead(event) {
      this.selectedLead = event.target.value
    },
    async stall() {
      await Lead.api.stallInStage(this.selectedLead)
    },
    async delay() {
      await Lead.api.delayCloseDate(this.selectedLead, this.selectedDays)
    },
    async inactive() {
      await Lead.api.clearLog(this.selectLead)
    },
  },
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
