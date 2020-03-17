<template>
  <div class="insights">
    LeadInsights Component
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
}
</style>
