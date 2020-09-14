<template>
  <div class="notification-page-container">
    <template v-if="notifications.list.length > 0">
      <template v-for="(value, key) in formattedNotifications(this.notifications.list)">
        <span class="muted" :key="key">
          {{ key }}
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
    async markAsViewed(notification) {
      await Notification.api.markAsViewed([notification.id])
      notification.viewed = true
      this.$emit('viewed-notif')
    },
    formattedNotifications(list) {
      if (list.length <= 0) {
        return null
      }
      let accumulator = {
        today: [],
        yesterday: [],
        'this week': [],
        'last week': [],
        'previous weeks': [],
      }
      return list.reduce((acc, curr) => {
        let today = moment()
        let yesterday = moment().subtract(1, 'day')
        let thisWeek = moment().startOf('week')
        let lastWeek = moment()
          .subtract(1, 'weeks')
          .startOf('week')
        let formatted = moment(curr.notifiedAt)
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
      }, accumulator)
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
