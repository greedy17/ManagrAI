<template>
  <div>Organization Performance Report</div>
</template>

<script>
import PerformanceReport from '@/services/performanceReports'

export default {
  name: 'OrganizationPerformanceReport',
  props: {
    report: {
      required: true,
      type: PerformanceReport,
    },
  },
  created() {},
  methods: {},
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
</style>
