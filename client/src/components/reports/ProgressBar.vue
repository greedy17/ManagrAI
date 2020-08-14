<template>
  <div class="progress-bar">
    <div ref="progress" class="progress" />
    <div class="center-piece" />
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    percentComplete: {
      type: Number,
      required: true,
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
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

$bar-width: 15rem;
$bar-height: 0.7rem;

.progress-bar {
  background-color: $soft-gray;
  border-radius: 13px; /* (height of inner div) / 2 + padding */
  width: $bar-width;
  height: $bar-height;

  position: relative;
  display: flex;
  flex-flow: column;
  justify-content: center;
}

.progress-bar > .progress {
  background-color: $dark-green;
  width: 0%; /* Adjust with JavaScript */
  height: $bar-height;
  border-radius: 10px;
  position: absolute;
}

.center-piece {
  background-color: $black;
  width: 0.3rem;
  height: $bar-height * 2;
  position: absolute;
  margin-left: $bar-width / 2;
  z-index: 1;
  border-radius: 1rem;
}
</style>
