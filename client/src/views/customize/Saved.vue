<template>
  <div class="customizations">
    <h1 style="color: red; text-align: center">IN PROGRESS, TESTING SAVED</h1>
  </div>
</template>
<script>
export default {
  name: 'Saved',
  data() {
    return {}
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.customizations {
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 4rem;
  &__cards {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
  }
  &__subtitle {
    font-size: 14px;
    margin-bottom: 2rem;
  }
}
</style>