<template>
  <div
    class="list-container"
    :class="{
      'list-container--horizontal': isHorizonal,
      'list-container--vertical': isVertical,
    }"
  >
    <div
      class="list-container__list"
      :class="{
        'list-container__list--horizontal': isHorizonal,
        'list-container__list--vertical': isVertical,
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
.list-container {
  position: inherit;
  background-color: white;
  -moz-box-shadow: inset 0 0 10px lightgray;
  -webkit-box-shadow: inset 0 0 10px lightgray;
  box-shadow: inset 0 0 10px lightgray;
  border-radius: 2px;
  color: white;
  width: 100%;

  &__list {
    &--horizontal {
      padding: 0.5rem 1rem;
      width: 100%;
      display: flex;
      height: 20rem;
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
