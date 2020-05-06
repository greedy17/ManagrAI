<template>
  <div class="spinner">
    <div class="spinner-a"></div>
    <div class="spinner-b"></div>
    <div class="spinner-c"></div>
  </div>
</template>

<script>
export default {
  name: 'ComponentLoadingSVG',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/animations';

.spinner {
  margin: 0 auto;
  width: 70px;
  text-align: center;

  & > div {
    // Bouncing circles
    width: 18px;
    height: 18px;
    border-radius: 100%;
    background-color: $base-gray;
    display: inline-block;
    @include extreme-pulse-animation();
  }

  & .spinner-a {
    animation-delay: -0.32s;
    background-color: $coral;
  }

  & .spinner-b {
    animation-delay: -0.16s;
    background-color: $yellow;
  }

  & .spinner-c {
    background-color: $dark-green;
  }
}
</style>
