<template>
  <div class="notification-page-container">
    <template v-if="notifications.list.length > 0 && datedNotifications">
      <template v-for="(value, key) in formattedNotifications(this.notifications.list)">
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
        model="Notification"
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
  },
  async created() {
    await this.notifications.refresh()
  },
  methods: {
    async markAsViewed(notificationId) {
      await Notification.api.markAsViewed([notificationId])
    },
    formattedNotifications(list) {
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
        let formatted = moment(curr.notifiedAt)
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
