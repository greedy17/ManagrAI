<template>
  <div class="checkbox" @click.stop.prevent="handleClick">
    <img v-if="checked" alt="checked" src="@/assets/images/check-box-checked.svg" />
    <img v-else alt="empty" src="@/assets/images/check-box-empty.svg" />
  </div>
</template>

<script>
export default {
  name: 'CheckBox',
  props: {
    checked: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    handleClick() {
      this.$emit('checkbox-clicked', !this.checked)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/utils';

.checkbox {
  @include pointer-on-hover();
  height: 1.5rem;
  width: 1.5rem;
  img {
    height: 1.5rem;
    width: 1.5rem;
  }
}
</style>
