<template>
  <div class="container" style="margin-top: 2rem;">
    <div class="box">
      <div class="box__header" ref="header">
        <div class="box__title">Previous Reports</div>
      </div>
      <div class="box__content">
        <template v-if="performanceReports.list.length">
          <div class="report" v-for="report in performanceReports.list" :key="report.id">
            <div class="report__focus">
              {{ getReportFocus(report) }},
              {{ report.dateRangePreset | consantToCapitalized }}
            </div>
            <div class="report__datetime">
              {{ report.datetimeCreated | dateShort }}
            </div>
            <button
              class="report__button"
              :disabled="!report.isReady"
              @click.prevent="openReport(report)"
            >
              {{ report.isReady ? 'See Report' : 'Pending...' }}
            </button>
          </div>
        </template>
        <template v-else>
          <div class="report">
            No Reports
          </div>
        </template>
      </div>
    </div>
    <Pagination
      v-if="!performanceReports.refreshing"
      :collection="performanceReports"
      :model="'Report'"
      @start-loading="startPaginationLoading($refs.header)"
      @end-loading="pagination.loading = false"
    />
  </div>
</template>

<script>
import Pagination from '@/components/shared/Pagination'
import { paginationMixin } from '@/services/pagination'

export default {
  name: 'PreviousPerformanceReports',
  mixins: [paginationMixin],
  components: {
    Pagination,
  },
  props: {
    performanceReports: {
      type: Object,
      required: true,
    },
  },
  methods: {
    getReportFocus(report) {
      if (report.representative) {
        let { fullName, email } = report.representativeRef
        return fullName.trim() ? fullName : email
      } else {
        return 'Organization-wide'
      }
    },
    openReport(report) {
      let routeData = this.$router.resolve({
        name: 'PerformanceReportDetail',
        params: { id: report.id },
      })
      window.open(routeData.href, '_blank')
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';

.container {
  width: 50vw;
}

.box__content {
  padding-left: 3em;
  padding-right: 3em;
}

.report {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1rem 0;
  color: $main-font-gray;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;

  &__focus {
    width: 45%;
  }
  &__button {
    @include primary-button;
    margin-left: auto;
    margin-right: 0;
  }
}
</style>
