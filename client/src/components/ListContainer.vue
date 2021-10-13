<template>
  <div class="ls-container">
    <div
      class="ls-container__list"
      :class="{
        'ls-container__list--horizontal': isHorizonal,
        'ls-container__list--vertical': isVertical,
      }"
    >
      <slot name="list"> </slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ListContainer',
  props: {
    item: String,
  },
  computed: {
    isHorizonal() {
      return this.$attrs.hasOwnProperty('horizontal')
    },
    isVertical() {
      return !this.isHorizonal || this.$attrs.hasOwnProperty('vertical')
    },
  },
}
</script>

<style scoped lang="scss">
.ls-container {
  background-color: white;
  border-radius: 0.25rem;
  color: white;
  width: 100%;
  height: 2.5rem;

  &__list {
    &--horizontal {
      padding: 0.5rem 1rem;
      width: 100%;
      display: flex;
      //flex-direction: row;
      overflow-x: scroll;
    }
    &--vertical {
      width: 100%;
      display: flex;
      flex-direction: column;
      padding: 0.5rem 1rem;
    }
  }
}
</style>
