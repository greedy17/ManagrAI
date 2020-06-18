<template>
  <div
    class="action-tab"
    :class="{ 'box__tab--active': active, box__tab: !active }"
    @click="handleClick"
  >
    <slot>
      <!-- header text -->
    </slot>
  </div>
</template>

<script>
export default {
  name: 'ActionTabHeader',
  props: {
    active: Boolean,
    index: Number,
  },
  methods: {
    handleClick() {
      this.$emit('update-active-tab', this.index)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/containers';

.action-tab {
  text-transform: capitalize;
}
</style>
