<template>
  <div
    class="popover"
    v-if="visible"
    :style="{ top: `${position.top}px`, left: `${position.left}px` }"
  >
    <slot></slot>
  </div>
</template>

<script>
export default {
  data() {
    return {
      visible: false,
      position: {
        top: 0,
        left: 0,
      },
    }
  },
  methods: {
    show(event) {
      this.position.top = event.clientY - 50 // Adjust positioning as needed
      this.position.left = event.clientX + 10 // Adjust positioning as needed
      this.visible = true
    },
    hide() {
      this.visible = false
    },
  },
}
</script>

<style scoped>
.popover {
  position: absolute;
  z-index: 1000;
  padding: 6px 2px;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  width: 100px;
  background-color: #8a7aaf;
  color: white;
  text-align: center;
  font-size: 14px;
  margin-left: -50px;
  pointer-events: none;
  transition: opacity 0.3s;
}
</style>
