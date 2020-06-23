<template>
  <div class="lead-history">
    <ActivityLogItem v-for="log in history.list" :key="log.id" :log="log" />

    <div v-if="refreshedOnce && !apiFailing && history.list.length === 0">
      <p>No actions have been taken on this opportunity.</p>
    </div>

    <div v-if="refreshedOnce && apiFailing">
      <p>We're having trouble retrieving this lead's history. Please try again later.</p>
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
    this.refresh()

    // Start polling for history
    this.pollingInterval = setInterval(this.refresh, 2000)
  },
  destroyed() {
    clearInterval(this.pollingInterval)
  },
  methods: {
    refresh() {
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
        })
        .catch(error => {
          console.log('HANDLING ERROR:', error)
          this.apiFailing = true
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
      clearInterval(this.pollingInterval)
      this.history.addNextPage()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
</style>
