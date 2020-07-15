<template>
  <div class="notification-page-container">
    <div class="notifications-list">
      <template v-for="(notification, i) in notifications.list">
        <NotificationCard :key="i" :notification="notification" />
      </template>
    </div>
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
    async refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      try {
        await this.notifications.refresh()
        if (repeat) {
          this.polllingTimeout = setTimeout(() => this.refresh(POLLING_INTERVAL), repeat)
        }
      } catch (e) {
        this.apiFailing = true
        if (repeat) {
          this.pollingTimeout = setTimeout(() => this.refresh(repeat * 2), repeat * 2)
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
