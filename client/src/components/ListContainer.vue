<template>
  <div class="list-container">
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
  padding: 0.5rem 1rem;
  height: 2.5rem;
  &__list {
    &--horizontal {
      width: 100%;
      display: flex;
      //flex-direction: row;
      overflow-x: scroll;
    }
  }
}
</style>
