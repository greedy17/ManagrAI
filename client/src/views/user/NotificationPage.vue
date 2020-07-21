<template>
  <div class="notification-page-container">
    <template v-if="notifications.list.length > 0">
      <template v-for="(notification, i) in notifications.list">
        <NotificationCard
          @mark-as-viewed="markAsViewed"
          :key="notification + '-' + i"
          :notification="notification"
        />
      </template>
    </template>
    <template v-else>
      No Notifications
    </template>
  </div>
</template>

<script>
import NotificationCard from '@/components/NotificationCard'
import Notification from '@/services/notifications/'
import CollectionManager from '@/services/collectionManager'

const POLLING_INTERVAL = 10000
export default {
  name: 'NotificationPage',
  components: { NotificationCard },
  data() {
    return {
      notifications: CollectionManager.create({ ModelClass: Notification }),

      pollingTimeout: null,
    }
  },
  async created() {
    await this.refresh(POLLING_INTERVAL)
  },
  methods: {
    async markAsViewed(notificationId) {
      await Notification.api.markAsViewed([notificationId])
    },

    async refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      try {
        await this.notifications.refresh()

        if (repeat) {
          this.polllingTimeout = setTimeout(async () => {
            this.refresh(POLLING_INTERVAL)
          }, repeat)
        }
      } catch (e) {
        this.apiFailing = true
        if (repeat) {
          this.pollingTimeout = setTimeout(async () => {
            this.refresh(repeat * 2)
          }, repeat * 2)
        }
      }
    },
  },

  destroyed() {
    clearTimeout(this.pollingTimeout)
  },
}
</script>

<style lang="scss" scoped></style>
