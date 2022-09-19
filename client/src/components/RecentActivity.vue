<template>
  <div class="recent-activity">
    <p class="gray-blue">Recent Activity</p>
    <small>You dont have any recent activity</small>
  </div>
</template>
<script>
export default {
  name: 'RecentActivity',
  data() {
    return {}
  },

  computed: {},
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';

.recent-activity {
  display: flex;
  flex-direction: column;
  padding: 4px 20px;
  color: $base-gray;
}
.gray-blue {
  color: $light-gray-blue;
  font-size: 14px;
}
</style>