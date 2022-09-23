<template>
  <div class="recent-activity">
    <p class="gray-blue">Recent Activity</p>
    <!-- <div>
      

    <small>Nothing here. Try making an update</small>
    </div> -->

    <div class="empty-list">
      <section class="bg-img"></section>
      <h4>Nothing here</h4>
      <p>Try making an update.</p>
      <button @click="refreshCalEvents" class="green_button">Open Pipeline</button>
    </div>
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

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $light-gray-blue;
  letter-spacing: 0.76px !important;

  .bg-img {
    background-image: url(../assets/images/logo.png);
    background-repeat: no-repeat;
    background-size: contain;
    background-position: center;
    height: 48px;
    width: 80px;
    opacity: 0.5;
  }
  h4 {
    color: $base-gray;
    margin-bottom: 0;
    margin-top: 12px;
  }
  p {
    font-size: 13px;
  }
}
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
.green_button {
  color: white;
  background-color: $dark-green;
  max-height: 2rem;
  border-radius: 8px;
  padding: 0.5rem 1.25rem;
  font-weight: bold;
  font-size: 12px;
  border: none;
  cursor: pointer;
}
</style>