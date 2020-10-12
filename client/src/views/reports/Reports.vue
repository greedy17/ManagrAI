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
          <!-- <div
          class="toolbar__row WIP"
          @click="() => {}"
          :class="{ toolbar__active: performanceReportsActive }"
        > -->
          Performance Reports
        </div>
      </div>
    </div>
    <div class="page__main-content-area" style="padding: 1rem;">
      <GenerateStoryReport v-if="storyReportsActive" :representatives="representatives" />
      <GeneratePerformanceReport
        v-if="performanceReportsActive"
        :representatives="representatives"
        @performance-report-created="prependNewPerformanceReport"
      />
      <PreviousPerformanceReports
        v-if="performanceReportsActive"
        :performanceReports="performanceReports"
      />
    </div>
  </div>
</template>

<script>
import CollectionManager from '@/services/collectionManager'
import User from '@/services/users'
import PerformanceReport from '@/services/performanceReports'
import { loadEntireCollection } from '@/services/utils'

import GenerateStoryReport from '@/components/reports/GenerateStoryReport'
import GeneratePerformanceReport from '@/components/reports/GeneratePerformanceReport'
import PreviousPerformanceReports from '@/components/reports/PreviousPerformanceReports'

export default {
  name: 'Reports',
  components: {
    GenerateStoryReport,
    GeneratePerformanceReport,
    PreviousPerformanceReports,
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
      performanceReports: CollectionManager.create({
        ModelClass: PerformanceReport,
      }),
    }
  },
  created() {
    loadEntireCollection(this.representatives)
    this.performanceReports.refresh()
  },
  methods: {
    toggleActivePage(pageToActivate) {
      this.storyReportsActive = false
      this.performanceReportsActive = false
      if (pageToActivate === 'storyReports') this.storyReportsActive = true
      if (pageToActivate === 'performanceReports') this.performanceReportsActive = true
    },
    prependNewPerformanceReport(report) {
      this.performanceReports.list.unshift(report)
      this.performanceReports.pagination.totalCount += 1
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
// .WIP {
//   cursor: not-allowed !important;
//   color: $mid-gray;
// }
</style>
