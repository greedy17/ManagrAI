<template>
  <div class="page">
    <PageLoadingSVG v-if="loading" />
    <div class="not-available" v-else-if="show404">
      <h1>404</h1>
      <p>Report Not Found</p>
    </div>
    <div class="not-available" v-else-if="!report.datetimeGenerated">
      <p>This report is still being generated.</p>
    </div>
    <div class="report shadow" v-else>
      <div class="divider" />
      <RepresentativePerformanceReport :report="report" v-if="report.isRepresentativeReport" />
      <OrganizationPerformanceReport :report="report" v-else />
      <div class="managr-logo">
        <img src="@/assets/images/logo-with-name.png" />
      </div>
    </div>
  </div>
</template>

<script>
import PerformanceReport from '@/services/performanceReports'

import RepresentativePerformanceReport from '@/components/reports/RepresentativePerformanceReport'
import OrganizationPerformanceReport from '@/components/reports/OrganizationPerformanceReport'

export default {
  name: 'PerformanceReportDetail',
  components: {
    RepresentativePerformanceReport,
    OrganizationPerformanceReport,
  },
  props: ['id'],
  data() {
    return {
      loading: true,
      show404: false,
      report: null,
    }
  },
  created() {
    PerformanceReport.api
      .retrieve(this.id)
      .then(report => {
        this.report = report
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
  computed: {
    missingReport() {
      return this.report === null
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
.page {
  padding: 0 10vw;
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
.managr-logo {
  text-align: center;

  img {
    height: 10rem;
  }
}
</style>
