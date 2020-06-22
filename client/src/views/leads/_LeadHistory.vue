<template>
  <div class="lead-history">
    <ActivityLogItem v-for="log in history.list" :key="log.id" :log="log" />

    <div v-if="!history.refreshing && history.list.length === 0">
      <p>No actions have been taken on this opportunity.</p>
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
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import LeadActivityLog from '@/services/leadActivityLogs'

import ActivityLogItem from './_ActivityLogItem'

export default {
  name: 'LeadHistory',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    ActivityLogItem,
  },
  data() {
    return {
      history: CollectionManager.create({
        ModelClass: LeadActivityLog,
        filters: {
          lead: this.lead.id,
        },
      }),
    }
  },
  created() {
    this.refresh()

    // Start polling for history
    // TODO: If this starts failing for any reason, it will start pumping out
    //       error messages, so we might want to clear or extend the interval
    //       if that happens.
    this.pollingInterval = setInterval(this.refresh, 2000)
  },
  destroyed() {
    clearInterval(this.pollingInterval)
  },
  methods: {
    refresh() {
      this.history.refresh()
    },
    addPage() {
      // TODO: This conflicts with polling, so we'll have to figure
      //       out how to handle that. For now, we disable polling
      //       if the user loads the next page, because they are
      //       looking for something old, not new.
      clearInterval(this.pollingInterval)
      this.history.addNextPage()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
</style>
