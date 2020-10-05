<template>
  <div>Representative Performance Report</div>
</template>

<script>
import PerformanceReport from '@/services/performanceReports'

export default {
  name: 'RepresentativePerformanceReport',
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
