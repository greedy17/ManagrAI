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

import ActivityLogItem from './_ActivityLogItem'

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
    history: {
      type: CollectionManager,
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
      hasNextPageData: false,
    }
  },
  watch: {
    async shouldRefreshPolling(val) {
      if (val) {
        if (
          this.$store.getters.pollingDataToUpdate.includes(`leadActivityLog:${this.lead.id}`) &&
          !this.hasNextPageData
        ) {
          await this.history.refresh()
        }
      }
    },
  },
  created() {
    this.$store.commit('UPDATE_ITEMS_TO_POLL', `leadActivityLog:${this.lead.id}`)
    this.history.refresh()
  },
  computed: {
    shouldRefreshPolling() {
      return this.$store.getters.updatePollingData
    },
  },
  destroyed() {
    clearTimeout(this.pollingTimeout)
    this.$store.commit('REMOVE_ITEMS_FROM_POLL', `leadActivityLog:${this.lead.id}`)
  },
  methods: {
    addPage() {
      // TODO: This conflicts with polling, so we'll have to figure
      //       out how to handle that. For now, we disable polling
      //       if the user loads the next page, because they are
      //       looking for something old, not new.
      this.hasNextPageData = true
      this.history.addNextPage()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
</style>
