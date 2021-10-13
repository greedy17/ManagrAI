<template>
  <div
    class="progress-bar"
    :style="{ width: `${widthValue}${widthUnit}`, height: `${heightValue}${heightUnit}` }"
  >
    <div ref="progress" class="progress" :style="{ height: `${heightValue}${heightUnit}` }" />
    <div
      class="center-piece"
      v-if="centerPiece"
      :style="{
        height: `${heightValue * 2}${heightUnit}`,
        marginLeft: `${widthValue / 2}${widthUnit}`,
      }"
    />
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    percentComplete: {
      required: true,
    },
    centerPiece: {
      type: Boolean,
      default: true,
    },
    heightValue: {
      default: 0.7,
    },
    heightUnit: {
      type: String,
      default: 'rem',
    },
    widthValue: {
      default: 20,
    },
    widthUnit: {
      type: String,
      default: 'vw',
    },
  },
  created() {
    setTimeout(this.config, 0)
  },
  methods: {
    config() {
      this.$refs.progress.style.width = `${this.roundedPercentage}%`
    },
  },
  computed: {
    roundedPercentage() {
      return Math.round(this.percentComplete)
    },
  },
  watch: {
    percentComplete() {
      this.config()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.progress-bar {
  background-color: $soft-gray;
  border-radius: 13px; /* (height of inner div) / 2 + padding */

  position: relative;
  display: flex;
  flex-flow: column;
  justify-content: center;
}

.progress-bar > .progress {
  background-color: $dark-green;
  width: 0%; /* Adjust with JavaScript */
  border-radius: 10px;
  position: absolute;
}

.center-piece {
  background-color: $black;
  width: 0.3rem;
  position: absolute;
  z-index: 1;
  border-radius: 1rem;
}
</style>
