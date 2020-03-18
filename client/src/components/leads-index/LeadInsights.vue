<template>
  <div class="insights">
    <div class="insights-header">
      <span class="insights-header-title">Insights</span>
      <div class="insights-header-link-container">
        <span class="insights-header-link">See All Detail</span>
      </div>
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

.insights-header-link-container {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.insights-header-link {
  text-transform: uppercase;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-weight: bold;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: #199e54;

  &:hover {
    cursor: pointer;
    border-radius: 5px;
    padding: 4px 6px;
    background-color: #199e54;
    color: #ffffff;
  }
}
</style>
