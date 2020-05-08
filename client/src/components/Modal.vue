<template>
  <div class="container" :class="{ dimmed: dimmed }" @click="emitCloseModal">
    <div
      class="modal"
      :class="{ 'box-shadow': !dimmed }"
      :style="{ height: `${height}vh`, width: `${width}vw` }"
      @click="stopPropagation"
    >
      <div class="content">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    dimmed: {
      type: Boolean,
      default: false,
    },
    height: {
      type: Number,
      default: 80,
    },
    width: {
      type: Number,
      default: 60,
    },
  },
  data() {
    return {
      currentY: window.scrollY,
    }
  },
  mounted() {
    window.addEventListener('scroll', this.noScroll)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.noScroll)
  },
  methods: {
    noScroll() {
      window.scrollTo(0, this.currentY)
    },
    emitCloseModal() {
      this.$emit('close-modal')
    },
    stopPropagation(e) {
      e.stopPropagation()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.container {
  position: absolute;
  left: 0;
  top: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
  display: flex;
  flex-flow: column;
  align-items: center;
  justify-content: center;
}

.dimmed {
  background-color: rgba($color: $black, $alpha: 0.5);
}

.modal {
  @include standard-border();
  z-index: 1001;
  background: $white;
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
}

.content {
  margin: 1rem;
  height: inherit;
  // width: inherit;
  border: 1px dashed black;
  overflow-y: auto;
}

.box-shadow {
  box-shadow: 0 4px 16px 0 rgba($color: $black, $alpha: 0.3);
}
</style>
