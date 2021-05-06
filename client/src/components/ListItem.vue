<template>
  <div
    @click="$emit('item-selected', item), $emit('click', $event)"
    class="item-container"
    :class="{ 'item-container--active': active }"
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
  width: 10rem;
  padding: 0.2rem 1rem;
  font-size: 13px;
  font-weight: bold;
  margin: 0rem 0.2rem;
  &--active {
    background-color: #199e54;
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
