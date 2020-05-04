<template>
  <div class="svg-container">
    <svg
      class="svg"
      :style="{ stroke: color }"
      width="200"
      height="200"
      viewBox="0 0 45 45"
      stroke="#000000"
    >
      <g fill="none" fill-rule="evenodd" transform="translate(1 1)" stroke-width="2">
        <circle cx="22" cy="22" r="12.2884" stroke-opacity="0">
          <animate
            attributeName="r"
            begin="1.5s"
            dur="3s"
            values="6;22"
            calcMode="linear"
            repeatCount="indefinite"
          />
          <animate
            attributeName="stroke-opacity"
            begin="1.5s"
            dur="3s"
            values="1;0"
            calcMode="linear"
            repeatCount="indefinite"
          />
          <animate
            attributeName="stroke-width"
            begin="1.5s"
            dur="3s"
            values="2;0"
            calcMode="linear"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="22" cy="22" r="20.2884" stroke-opacity="0">
          <animate
            attributeName="r"
            begin="3s"
            dur="3s"
            values="6;22"
            calcMode="linear"
            repeatCount="indefinite"
          />
          <animate
            attributeName="stroke-opacity"
            begin="3s"
            dur="3s"
            values="1;0"
            calcMode="linear"
            repeatCount="indefinite"
          />
          <animate
            attributeName="stroke-width"
            begin="3s"
            dur="3s"
            values="2;0"
            calcMode="linear"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="22" cy="22" r="4.71631">
          <animate
            attributeName="r"
            begin="0s"
            dur="1.5s"
            values="6;1;2;3;4;5;6"
            calcMode="linear"
            repeatCount="indefinite"
          />
        </circle>
      </g>
    </svg>
  </div>
</template>

<script>
const DARK_GREEN = '#199e54' // $dark-green
const LIME_GREEN = '#78c142' // $lime-green
const YELLOW = '#fab900' // $yellow
const CORAL = '#fa646a' // $coral
const themeColors = [DARK_GREEN, LIME_GREEN, YELLOW, CORAL]
const color = themeColors[Math.floor(Math.random() * themeColors.length)]

export default {
  name: 'LoadingSVG',
  data() {
    return { color }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.svg-container {
  position: absolute;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  background-color: $white;
  z-index: 1000;

  .svg {
    position: absolute;
    top: 25vh;
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>
