<template>
  <div class="page">
    <PageLoadingSVG v-if="loading" />
    <div class="not-available" v-else-if="show404">
      <h1>404</h1>
      <p>Report Not Found</p>
    </div>
    <div class="not-available" v-else-if="!storyReport.datetimeGenerated">
      <p>This report is still being generated.</p>
    </div>
    <div class="report shadow" v-else>
      Page 1!!
      <div class="divider" />
      <div class="profile-photo-and-list">
        <div class="profile-photo">
          photo here
        </div>
        <div class="list">
          list here
        </div>
      </div>
      <div class="status-metrics">
        status metrics container
      </div>
      <div class="managr-logo">
        managr logo
      </div>
      <div class="divider" />
      <div class="actions">
        actions here
      </div>
      <div class="contract-hero">
        contract hero here
      </div>
      <div class="table">
        table here
      </div>
      <div class="managr-logo">
        managr logo
      </div>
    </div>
  </div>
</template>

<script>
import StoryReport from '@/services/storyReports'

export default {
  name: 'StoryReportDetail',
  components: {},
  props: ['id'],
  data() {
    return {
      loading: true,
      show404: false,
      storyReport: null,
    }
  },
  created() {
    StoryReport.api
      .retrieve(this.id)
      .then(report => {
        this.storyReport = report
      })
      .catch(({ response }) => {
        if (response.status === 404) {
          this.show404 = true
        }
      })
      .finally(() => {
        this.loading = false
      })
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/layout';
// @import '@/styles/containers';
// @import '@/styles/sidebars';
// @import '@/styles/mixins/utils';

.page {
  padding: 0 10rem;
}

.shadow {
  box-shadow: 0 0 5px 1px $soft-gray;
}

.report {
  background-color: $white;
}

.divider {
  background-color: $dark-green;
  height: 0.5em;
  width: 100%;
}

.not-available {
  padding-top: 10rem;
  color: $mid-gray;
  display: flex;
  flex-flow: column;
  align-items: center;
  h1 {
    font-size: 2rem;
  }
  p {
    font-size: 1.5rem;
    margin-top: 0;
  }
}
</style>
