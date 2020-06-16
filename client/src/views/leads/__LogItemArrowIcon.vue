<template>
  <img
    alt="icon"
    :src="require(`@/assets/images/dropdown-arrow.svg`)"
    class="icon dropdown-icon"
    :class="{ 'dropdown-icon--up': !down }"
  />
</template>

<script>
export default {
  name: 'LogItemArrowIcon',
  props: {
    down: Boolean,
  },
}
</script>

<style lang="scss">
.dropdown-icon {
  transition: transform ease 0.3s;
  transform: rotate3d(0);

  &--up {
    transform: rotate3d(0, 0, 1, 3.142rad);
  }
}
</style>
