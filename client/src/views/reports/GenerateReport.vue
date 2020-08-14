<template>
  <div class="page">
    <div class="page__left-nav-bar">
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
          class="toolbar__row WIP"
          @click="() => {}"
          :class="{ toolbar__active: performanceReportsActive }"
        >
          Performance Reports
        </div>
      </div>
    </div>
    <div class="page__main-content-area">
      <GenerateStoryReport v-if="storyReportsActive" />
    </div>
  </div>
</template>

<script>
import GenerateStoryReport from '@/components/reports/GenerateStoryReport'

export default {
  name: 'GenerateReport',
  components: {
    GenerateStoryReport,
  },
  data() {
    return {
      storyReportsActive: true,
      performanceReportsActive: false,
    }
  },
  methods: {
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

.WIP {
  color: $gray;
  &:hover {
    cursor: not-allowed;
  }
}
</style>
