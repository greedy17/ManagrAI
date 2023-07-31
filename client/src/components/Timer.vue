<template>
  <div>
    <div class="small-gray-text" v-if="remainingTime > 0">
      <p>({{ displayPercentage }})</p>
    </div>
    <div v-else>{{ finishMessage }}</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      startTime: null,
      timerInterval: null,
      duration: 180,
    }
  },
  props: {
    // duration: {},
    finishMessage: {},
  },
  computed: {
    remainingTime() {
      const now = Date.now()
      const startTime = this.startTime ? this.startTime : now
      const elapsedTime = Math.floor((now - startTime) / 1000)
      return Math.max(0, this.duration - elapsedTime)
    },
    displayPercentage() {
      let percentage = Math.floor((this.remainingTime / this.duration) * 100)
      return `${percentage}%`
    },
  },
  methods: {
    startTimer() {
      this.startTime = Date.now()
      localStorage.setItem('timerStartTime', this.startTime.toString())

      this.timerInterval = setInterval(() => {
        if (this.remainingTime === 0) {
          this.$emit('timer-finished')
          this.stopTimer()
          localStorage.removeItem('timerStartTime')
        }
      }, 1000)
    },
    stopTimer() {
      clearInterval(this.timerInterval)
      this.timerInterval = null
    },
  },
  mounted() {
    const storedStartTime = localStorage.getItem('timerStartTime')
    if (storedStartTime) {
      this.startTime = parseInt(storedStartTime)
      this.startTimer()
    } else {
      this.startTimer()
    }
  },
  beforeDestroy() {
    this.stopTimer()
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';

.small-gray-text {
  color: $light-gray-blue;
  font-size: 12px;
  margin-right: 1rem;
}
</style>
