<template>
  <div class="lead-emails">
    <div v-if="threads.refreshing" style="padding: 5rem;">
      <ComponentLoadingSVG v-if="threads.refreshing" />
    </div>

    <Thread
      @email-sent="refresh"
      :thread="thread"
      v-for="thread in threads.list"
      :key="thread.id"
      :lead="lead"
    ></Thread>

    <div v-if="!threads.refreshing && threads.list.length === 0">
      <p>No emails found for this opportunity.</p>
    </div>

    <button
      class="primary-button"
      @click="addPage"
      v-if="threads.hasNextPage"
      style="margin: 1rem"
      :disabled="threads.refreshing || threads.loadingNextPage"
    >
      Load More
    </button>
  </div>
</template>

<script>
import Thread from '@/components/emails/Thread'
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'

import Nylas from '@/services/nylas'

export default {
  name: 'LeadEmails',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    ComponentLoadingSVG,
    Thread,
  },
  data() {
    return {
      filters: {
        anyEmail: this.lead.linkedContactsRef.map(c => c.email).join(','),
        page: 1,
      },
      threads: {
        list: [],
        refreshing: false,
        loadingNextPage: false,
        hasNextPage: false,
      },
    }
  },
  created() {
    this.refresh()
  },
  methods: {
    /**
     * We presume that there is a next page if we get a full page of results.
     *
     * Nylas does not / cannot provide a total count of threads for us.
     * Their docs say that if the API returns less than the limit (that is, page size),
     * then there are no more results.
     */
    checkHasNextPage(result) {
      return result.length === 10
    },
    refresh() {
      this.threads.refreshing = true
      Nylas.getThreads({ filters: this.filters })
        .then(result => {
          this.threads.list = result
          this.threads.hasNextPage = this.checkHasNextPage(result)
        })
        .finally(() => {
          this.threads.refreshing = false
        })
    },
    addPage() {
      this.threads.loadingNextPage = true
      this.filters = {
        page: this.filters.page + 1,
        ...this.filters,
      }
      Nylas.getThreads({ filters: this.filters })
        .then(result => {
          this.threads.list = [...this.threads.list, ...result]
          this.threads.hasNextPage = this.checkHasNextPage(result)
        })
        .finally(() => {
          this.threads.loadingNextPage = false
        })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.primary-button {
  @include primary-button;
}
</style>
