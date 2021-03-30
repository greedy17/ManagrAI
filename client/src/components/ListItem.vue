<template>
  <div @click="$emit('item-selected', item)" class="item-container">
    <span class="item-container__label">{{ item }}</span>
  </div>
</template>

<script>
export default {
  name: 'ListItem',
  props: {
    item: String,
  },
}
</script>

<style scoped lang="scss">
.item-container {
  display: flex;
  flex: 0 0 auto;
  background-color: #199e54;
  border-radius: 2px;
  color: white;
  width: 10rem;
  padding: 0rem 1rem;
  font-size: 12px;
  font-weight: bold;
  margin: 0rem 0.2rem;
  &:hover {
    cursor: pointer;
  }
  &__label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
