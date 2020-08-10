<template>
  <div class="notification-page-container">
    <template v-if="notifications.list.length > 0 && datedNotifications">
      <template v-for="(value, key) in datedNotifications">
        <span class="muted" :key="key"
          >{{ key }}
          <br />
        </span>

        <NotificationCard
          v-for="(item, i) in value"
          @mark-as-viewed="markAsViewed"
          :key="item.id"
          :notification="item"
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
import moment from 'moment'

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
  watch: {
    async shouldRefreshPolling(val) {
      if (val) {
        await this.notifications.refresh()
      }
    },
  },
  computed: {
    shouldRefreshPolling() {
      return this.$store.getters.updatePollingData
    },
    datedNotifications() {
      if (this.notifications.list.length <= 0) {
        return null
      }
      return this.notifications.list.reduce((acc, curr) => {
        let today = moment()

        let formatted = moment(curr.notifyAt)
        console.log(acc)
        if (!acc['today']) {
          acc['today'] = []
        }
        if (today.isSame(formatted, 'day')) {
          acc['today'].push(curr)
          return acc
        } else if (formatted.isSame(acc[moment(curr.notifyAt)], 'day')) {
          acc[moment(curr.notifyAt).format('MMMM Do YYYY')].push(curr)
          return acc
        } else {
          acc[moment(curr.notifyAt).format('MMMM Do YYYY')] = [curr]
          return acc
        }
      }, {})
    },
  },
  async created() {
    await this.notifications.refresh()
  },
  methods: {
    async markAsViewed(notificationId) {
      await Notification.api.markAsViewed([notificationId])
    },
    async getNextPage() {
      await this.notifications.addNextPage()
    },
  },

  destroyed() {
    clearTimeout(this.pollingTimeout)
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.muted {
  text-transform: capitalize;
}
</style>
