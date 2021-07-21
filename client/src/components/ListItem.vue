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
  color: #cc3873;
  padding: 0.2rem 0.5rem;
  font-size: 13px;
  font-weight: bold;
  margin: 0rem 0.1rem;
  &--active {
    background-color: transparent;
    margin-left: -1rem;
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
    text-overflow: ellipsis;
    border-bottom: 1px solid #cc3873;
  }
  &__icon {
  }
}
</style>
