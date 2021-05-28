<template>
  <div class="alerts-dashboard">
    <AlertsDashboardMenu />
  </div>
</template>

<script>
import AlertsDashboardMenu from '@/views/settings/alerts/_AlertsDashboardMenu'
export default {
  name: 'AlertsDashboard',
  components: { AlertsDashboardMenu },
}
</script>

<style lang="scss" scoped>
.alerts-dashboard {
  padding: 0 8rem;
}
</style>
