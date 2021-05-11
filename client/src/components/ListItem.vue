<template>
  <div
    @click="$emit('item-selected', item), $emit('click', $event)"
    class="item-container"
    :class="{
      'item-container--active': active,
      'item-container--small': isSmall || (!isMedium && !isLarge && !isAutoSize),
      'item-container--medium': isMedium,
      'item-container--large': isLarge,
    }"
  >
    <span class="item-container__label">{{ item }}</span>
    <span v-if="showIcon" class="item-container__icon">x</span>
  </div>
</template>

<script>
export default {
  name: 'ListItem',
  props: {
    item: String,
    active: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    showIcon() {
      return this.$attrs.hasOwnProperty('showIcon')
    },
    isSmall() {
      return this.$attrs.hasOwnProperty('small')
    },
    isMedium() {
      return this.$attrs.hasOwnProperty('medium')
    },
    isLarge() {
      return this.$attrs.hasOwnProperty('large')
    },
    isAutoSize() {
      return this.$attrs.hasOwnProperty('autoSize')
    },
  },
}
</script>

<style scoped lang="scss">
.item-container {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex: 0 0 auto;
  background-color: lightgray;
  border-radius: 2px;
  color: white;

  padding: 0.2rem 1rem;
  font-size: 13px;
  font-weight: bold;
  margin: 0rem 0.2rem;
  &--active {
    background-color: #199e54;
  }
  &--small {
    width: 10rem;
  }
  &--medium {
    width: 20rem;
  }
  &--large {
    width: 30rem;
  }

  &:hover {
    cursor: pointer;
  }
  &__label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  &__icon {
  }
}
</style>
