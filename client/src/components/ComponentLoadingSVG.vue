<template>
  <div class="spinner">
    <div class="spinner-a" :style="{ backgroundColor: color }"></div>
    <div class="spinner-b" :style="{ backgroundColor: color }"></div>
    <div class="spinner-c" :style="{ backgroundColor: color }"></div>
  </div>
</template>

<script>
const DARK_GREEN = '#199e54' // $dark-green
const LIME_GREEN = '#78c142' // $lime-green
const YELLOW = '#fab900' // $yellow
const CORAL = '#fa646a' // $coral
const themeColors = [DARK_GREEN, YELLOW, CORAL]
const color = themeColors[Math.floor(Math.random() * themeColors.length)]

export default {
  name: 'ComponentLoadingSVG',
  data() {
    return { color }
  },
}
</script>

<style lang="scss" scoped>
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
    display: inline-block;
    @include extreme-pulse-animation();
  }

  & .spinner-a {
    animation-delay: -0.32s;
  }

  & .spinner-b {
    animation-delay: -0.16s;
  }
}
</style>
