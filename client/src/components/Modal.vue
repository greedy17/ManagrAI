<template>
  <div
    class="container"
    ref="container"
    :class="{ dimmed: dimmed }"
    :style="{ top: `${original.documentY}px` }"
    @click="emitCloseModal"
  >
    <div class="modal" :class="{ 'box-shadow': !dimmed }" :style="{ width: `${width}vw` }">
      <div :class="{ content: includeMargin }">
        <slot />
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @component Modal
 *
 * @contributors
 *   Bruno Garcia Gonzalez
 *
 * Custom modal that does not rely on any libraries.
 * Developer can just wrap their own code in this modal and leverage the <slot /> herein.
 * Clicking outside of the modal yields the emission of @close-modal,
 * so that this modal can be closed at the parent-level.
 * <body /> original overflow settings are tracked so that on-close styles can reset to original.
 *
 * @example
 *  <Modal v-if="modalIsOpen" :height="60" dimmed @close-modal="modalIsOpen = false">
 *      <p>Hello from inside of the modal!</p>
 *      <button @click="doStuffAndThenCloseModal">Do Thing and Close</button>
 *  </Modal>
 *
 * Props:
 *  @prop {Boolean} dimmed - Optional. Whether the background of the modal is dimmed or not. Defaults to false.
 *  @prop {Integer} width - Optional. How tall, in vw units, the modal should be. Defaults to 60.
 *
 * Events:
 *  @event close-modal - Emitted when the area of page around the actual modal is clicked.
 */
export default {
  name: 'Modal',
  props: {
    dimmed: {
      type: Boolean,
      default: false,
    },
    width: {
      type: Number,
      default: 60,
    },
    includeMargin: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      original: {
        documentY: document.documentElement.scrollTop,
        overflowX: document.body.style.overflowX,
        overflowY: document.body.style.overflowY,
      },
    }
  },
  mounted() {
    document.body.style.overflowX = 'hidden'
    document.body.style.overflowY = 'hidden'
  },
  beforeDestroy() {
    document.body.style.overflowX = this.original.overflowX
    document.body.style.overflowY = this.original.overflowY
  },
  methods: {
    emitCloseModal({ target }) {
      if (this.$refs.container === target) {
        this.$emit('close-modal')
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.container {
  position: absolute;
  left: 0;
  //   top: 0; This is calculated from componentState.original.documentY
  width: 100vw;
  height: 100vh;
  min-height: 100vh !important; // in case of inheritance issues
  z-index: 1000;
  display: flex;
  flex-flow: column;
  align-items: center;
  overflow-y: scroll;
}

.dimmed {
  background-color: rgba($color: $black, $alpha: 0.5);
}

.modal {
  margin: 8vh 0;
  border: 1px solid $soft-gray; // soft-gray
  z-index: 1001;
  background: $white;
  display: flex;
  flex-flow: column;
  box-sizing: border-box;
  height: auto;
}

.content {
  margin: 1rem;
  height: inherit;
}

.box-shadow {
  box-shadow: 0 4px 16px 0 rgba($color: $black, $alpha: 0.3);
}
</style>
