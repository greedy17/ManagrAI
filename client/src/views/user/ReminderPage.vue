<template>
  <div class="notification-page-container">
    <small class="muted">last checked at {{ lastChecked | dateShortWithTime }} </small>
    <br />
    <small class="muted"> to refresh toggle back </small>
    <br />
    <br />

    <template v-if="reminders.list.length > 0">
      <!-- start -->

      <template v-for="(value, key) in formattedReminders(reminders.list)">
        <span class="muted" :key="key">
          {{ key }}
          <br />
        </span>
        <template v-for="(reminder, i) in value">
          <ReminderCard @delete="onDelete" :key="reminder + '-' + i" :reminder="reminder" />
        </template>
      </template>

      <!-- end -->
    </template>
    <template v-else>
      <br />
      <br />

      No Upcoming Reminders
    </template>
  </div>
</template>

<script>
import ReminderCard from '@/components/ReminderCard'
import Reminder from '@/services/reminders/'
import CollectionManager from '@/services/collectionManager'
import moment from 'moment'

export default {
  name: 'ReminderPage',
  components: { ReminderCard },
  data() {
    return {
      // will not be auto refreshing to cut down on automatic calls
      // instead will show last checked time and tell user to toggle for refresh
      lastChecked: moment().format(),
      reminders: CollectionManager.create({
        ModelClass: Reminder,
        filters: {
          byRemindOn: moment().format(),
        },
      }),
    }
  },
  async created() {
    await this.reminders.refresh()
  },
  methods: {
    async onDelete(event) {
      try {
        await Reminder.api.delete(event)
        this.reminders.refresh()
      } catch (e) {
        return
      }
    },
    formattedReminders(list) {
      if (list.length <= 0) {
        return null
      }
      return list.reduce((acc, curr) => {
        let today = moment()
        let yesterday = moment().subtract(1, 'day')
        let thisWeek = moment().startOf('week')
        let lastWeek = moment()
          .subtract(1, 'weeks')
          .startOf('week')
        let formatted = moment(curr.datetimeCreated)
        if (!acc['today']) {
          acc['today'] = []
        }
        if (!acc['yesterday']) {
          acc['yesterday'] = []
        }
        if (!acc['this week']) {
          acc['this week'] = []
        }
        if (!acc['last week']) {
          acc['last week'] = []
        }
        if (!acc['previous weeks']) {
          acc['previous weeks'] = []
        }
        if (today.isSame(formatted, 'day')) {
          acc['today'].push(curr)
          return acc
        } else if (yesterday.isSame(formatted, 'day')) {
          acc['yesterday'].push(curr)
          return acc
        } else if (formatted.isSame(thisWeek, 'week')) {
          acc['this week'].push(curr)
          return acc
        } else if (formatted.isSame(lastWeek, 'week')) {
          acc['last week'].push(curr)
          return acc
        } else if (formatted.isBefore(lastWeek, 'week')) {
          acc['previous weeks'].push(curr)
          return acc
        }
      }, {})
    },
  },

  destroyed() {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.muted {
  text-transform: capitalize;
}
</style>
