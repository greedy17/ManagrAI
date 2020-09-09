<template>
  <div class="notification-page-container">
    <small class="muted">last checked at {{ lastChecked | dateShortWithTime }} </small>
    <br />
    <small class="muted"> to refresh toggle back </small>
    <br />
    <br />

    <template v-if="reminders.list.length > 0">
      <template v-for="(value, key) in formattedReminders(reminders.list)">
        <span class="muted" :key="key">
          {{ key }}
          <br />
        </span>
        <template v-for="(reminder, i) in value">
          <ReminderCard @delete="onDelete" :key="reminder + '-' + i" :reminder="reminder" />
        </template>
      </template>
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
      let accumulator = {
        today: [],
        tomorrow: [],
        future: [],
      }
      return list.reduce((acc, curr) => {
        let today = moment()
        let tomorrow = moment().add(1, 'day')
        let formatted = moment(curr.datetimeFor)
        if (today.isSame(formatted, 'day')) {
          acc['today'].push(curr)
          return acc
        } else if (tomorrow.isSame(formatted, 'day')) {
          acc['tomorrow'].push(curr)
          return acc
        } else if (formatted.isAfter(tomorrow, 'day')) {
          acc['future'].push(curr)
          return acc
        }
      }, accumulator)
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
