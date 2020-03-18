<template>
  <div class="insights">
    <div class="insights-header">
      <span class="insights-header-title">Insights</span>
      <span class="insights-header-link">See All Detail</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeadInsights',
  props: ['lead'],
}
</script>

<style lang="scss" scoped>
.insights {
  width: 255px;
  height: 325px;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px #f2f2f3;
  background-color: #ffffff;
  display: flex;
  flex-flow: column;
}

.insights-header {
  height: 48px;
  display: flex;
  flex-flow: row;
  align-items: center;
  box-shadow: 0 1px 0 0 #ececee;
}

.insights-header-title {
  flex-grow: 1;
  padding: 5% 0 5% 7%;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #110f24;
}

.insights-header-link {
  flex-grow: 1;
  text-transform: uppercase;
  text-align: right;
  padding: 5% 7% 5% 0%;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #199e54;
}
</style>
