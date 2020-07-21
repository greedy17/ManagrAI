<template>
  <div class="notification-page-container">
    <small>last checked at {{ lastChecked | dateShortWithTime }} to refresh toggle back</small>
    <template v-if="reminders.list.length > 0">
      <template v-for="(reminder, i) in reminders.list">
        <ReminderCard @delete="onDelete" :key="reminder + '-' + i" :reminder="reminder" />
      </template>
    </template>
    <template v-else>
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
  },

  destroyed() {},
}
</script>

<style lang="scss" scoped></style>
