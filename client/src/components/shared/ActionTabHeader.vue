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
  width: 91px;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 12px;
  font-stretch: normal;
  font-style: normal;
  line-height: 2;
  letter-spacing: normal;
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: capitalize;

  &:hover {
    cursor: pointer;
  }
}
</style>
