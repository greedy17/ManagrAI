<template>
  <div>
    <div v-if="showUpArrow" @click="scrollToTop" class="scroll-arrow up-arrow">↑</div>
    <div v-if="showDownArrow" @click="scrollToBottom" class="scroll-arrow down-arrow">↓</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showUpArrow: false,
      showDownArrow: false,
    }
  },
  methods: {
    handleScroll() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const scrollHeight = document.documentElement.scrollHeight
      const clientHeight = document.documentElement.clientHeight

      this.showUpArrow = scrollTop > 0
      this.showDownArrow = scrollTop + clientHeight < scrollHeight
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    scrollToBottom() {
      window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' })
    },
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
    this.handleScroll() // Initial check
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.handleScroll)
  },
}
</script>

<style scoped>
.scroll-arrow {
  position: absolute;
  bottom: 100px;
  cursor: pointer;
  font-size: 24px;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 10px;
  border-radius: 50%;
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
}
.up-arrow {
  left: 10px;
}
.down-arrow {
  right: 10px;
}
</style>
