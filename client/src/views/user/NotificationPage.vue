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
      <Pagination
        v-if="!notifications.refreshing"
        style="margin-bottom: 1rem;"
        :collection="notifications"
        @start-loading="hasNextPageData = true"
      />
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
import Pagination from '@/components/shared/Pagination'

export default {
  name: 'NotificationPage',
  components: { NotificationCard, Pagination },
  data() {
    return {
      notifications: CollectionManager.create({ ModelClass: Notification }),
      hasNextPageData: false,
      pollingTimeout: null,
    }
  },
  watch: {
    async shouldRefreshPolling(val) {
      if (val) {
        if (
          this.$store.getters.pollingDataToUpdate.includes('notification') &&
          !this.hasNextPageData
        ) {
          await this.notifications.refresh()
        }
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
