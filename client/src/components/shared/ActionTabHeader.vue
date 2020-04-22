<template>
  <div class="action-tab-header" :style="styles" @click="handleClick">
    <slot><!-- header text --></slot>
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
  computed: {
    styles() {
      if (this.active) {
        return {
          borderBottom: '2px solid #2F9E54',
          color: '#110f24',
          fontWeight: 'bold',
        }
      } else {
        return {
          borderBottom: 'unset',
          color: '#BCBCC1',
          fontWeight: 'normal',
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.action-tab-header {
  @include disable-text-select();
  @include pointer-on-hover();
  @include base-font-styles();
  width: 5.7rem;
  font-size: 12px;
  line-height: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: capitalize;
}
</style>
