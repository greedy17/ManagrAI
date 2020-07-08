<template>
  <div class="lead-history" ref="mainDiv">
    <ComponentLoadingSVG style="margin-top: 2rem; margin-bottom: 2rem;" v-if="activityLogLoading" />
    <template v-else>
      <div v-if="refreshedOnce && !apiFailing && history.list.length === 0">
        <p>No actions have been taken on this opportunity.</p>
      </div>

      <div v-if="refreshedOnce && apiFailing">
        <p>We're having trouble retrieving this lead's history. Please try again later.</p>
      </div>

      <div v-if="!apiFailing">
        <ActivityLogItem
          v-for="log in history.list"
          :key="log.id"
          :log="log"
          :expanded="expandedHistoryItems.includes(log.id)"
          @toggle-history-item="id => $emit('toggle-history-item', id)"
        />
      </div>

      <button
        class="primary-button"
        @click="addPage"
        v-if="history.pagination.hasNextPage"
        style="margin: 1rem"
        :disabled="history.loadingNextPage"
      >
        Load More
      </button>
    </template>
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import LeadActivityLog from '@/services/leadActivityLogs'

import ActivityLogItem from './_ActivityLogItem'

const POLLING_INTERVAL = 2000

export default {
  name: 'LeadHistory',
  props: {
    lead: {
      type: Object,
      required: true,
    },
    expandedHistoryItems: {
      type: Array,
      required: true,
    },
    activityLogLoading: {
      type: Boolean,
      required: true,
    },
  },
  components: {
    ActivityLogItem,
  },
  data() {
    return {
      refreshedOnce: false,
      apiFailing: false,
      history: CollectionManager.create({
        ModelClass: LeadActivityLog,
        filters: {
          lead: this.lead.id,
        },
      }),
    }
  },
  created() {
    this.refresh(POLLING_INTERVAL)
  },
  destroyed() {
    clearTimeout(this.pollingTimeout)
  },
  methods: {
    refresh(repeat) {
      clearTimeout(this.pollingTimeout)
      // Since we're polling, we want to suppress the default error handling,
      // because that produces a lot of error alert boxes. Instead, we set an
      // apiFailing flag, so we can show a custom error message.
      this.history
        .refresh({
          enable400Alert: false,
          enable500Alert: false,
        })
        .then(() => {
          this.apiFailing = false
          if (repeat) {
            this.pollingTimeout = setTimeout(() => this.refresh(POLLING_INTERVAL), repeat)
          }
        })
        .catch(error => {
          this.apiFailing = true
          if (repeat) {
            // Repeat with exponential back-off as long as calls are failing
            this.pollingTimeout = setTimeout(() => this.refresh(repeat * 2), repeat * 2)
          }
        })
        .finally(() => {
          this.refreshedOnce = true
        })
    },
    addPage() {
      // TODO: This conflicts with polling, so we'll have to figure
      //       out how to handle that. For now, we disable polling
      //       if the user loads the next page, because they are
      //       looking for something old, not new.
      clearTimeout(this.pollingTimeout)
      this.history.addNextPage()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
</style>
