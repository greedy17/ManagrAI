<template>
  <div class="page">
    <div class="page__left-nav-bar test" style="padding: 1rem;">
      <div class="toolbar">
        <div class="toolbar__header">
          <span class="toolbar__title">Reports</span>
        </div>
        <div
          class="toolbar__row"
          @click="toggleActivePage('storyReports')"
          :class="{ toolbar__active: storyReportsActive }"
        >
          Story Reports
        </div>
        <div
          class="toolbar__row"
          @click="toggleActivePage('performanceReports')"
          :class="{ toolbar__active: performanceReportsActive }"
        >
          Performance Reports
        </div>
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <GenerateStoryReport v-if="storyReportsActive" :representatives="representatives" />
      <GeneratePerformanceReport
        v-if="performanceReportsActive"
        :representatives="representatives"
      />
    </div>
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'

import GenerateStoryReport from '@/components/reports/GenerateStoryReport'
import GeneratePerformanceReport from '@/components/reports/GeneratePerformanceReport'

export default {
  name: 'GenerateReport',
  components: {
    GenerateStoryReport,
    GeneratePerformanceReport,
  },
  data() {
    return {
      storyReportsActive: true,
      performanceReportsActive: false,
      representatives: CollectionManager.create({
        ModelClass: User,
        filters: {
          byUser: this.$store.state.user.id,
        },
      }),
    }
  },
  created() {
    this.loadEntireCollection(this.representatives)
  },
  methods: {
    async loadEntireCollection(collection) {
      // Since the list of collection is for populating a dropdown, there is no pagination UI.
      // Yet, our backend delivers paginated results.
      // Therefore, continue to retrieve (and append) more results as long as this collection has a next page.
      await collection.refresh()
      while (collection.pagination.hasNextPage) {
        await collection.addNextPage()
      }
    },
    toggleActivePage(pageToActivate) {
      this.storyReportsActive = false
      this.performanceReportsActive = false
      if (pageToActivate === 'storyReports') this.storyReportsActive = true
      if (pageToActivate === 'performanceReports') this.performanceReportsActive = true
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/sidebars';
@import '@/styles/mixins/utils';

.toolbar__row {
  @include pointer-on-hover;
}
</style>
