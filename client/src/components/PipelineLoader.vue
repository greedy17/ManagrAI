<template>
  <div class="pipeline-loader">
    <div class="card">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" />
      <h1>Just a moment</h1>
      <p>Pulling in your latest Salesforce data</p>
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineLoader',
  data() {
    return {}
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.pipeline-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 70vh;
}
.table-sectioned {
  height: 76vh;
}
.flex-row-spreader {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  margin-top: 1rem;
}
</style>