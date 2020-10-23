<template>
  <div class="notification-page-container">
    <template v-if="notifications.list.length > 0">
      <button class="mark-all-as-viewed" @click="markAllAsViewed">MARK ALL AS READ</button>

      <template v-for="(value, key) in formattedNotifications(this.notifications.list)">
        <span class="muted" :key="key">
          {{ key }}
          <br />
        </span>

        <NotificationCard
          v-for="(item, i) in value"
          @mark-as-viewed="markAsViewed([item])"
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
import { loadEntireCollection } from '@/services/utils'

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
    async markAsViewed(notifications) {
      if (!notifications.length) {
        return
      }
      let ids = notifications.map(n => n.id)
      await Notification.api.markAsViewed(ids)
      if (notifications.length >= 25) {
        for (let n of this.notifications.list) {
          n.viewed = true
        }
      } else {
        for (let n of notifications) {
          n.viewed = true
        }
      }
      this.$emit('viewed-notif', notifications.length)
    },
    async markAllAsViewed() {
      let cloneCollection = this.notifications.shallowClone()
      cloneCollection.filters.wasViewed = false
      await loadEntireCollection(cloneCollection)
      let unviewed = cloneCollection.list.filter(n => !n.viewed)
      this.markAsViewed(unviewed)
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
@import '@/styles/mixins/buttons';

.muted {
  text-transform: capitalize;
}

.mark-all-as-viewed {
  @include secondary-button;
  margin: 1rem auto;
}
</style>
