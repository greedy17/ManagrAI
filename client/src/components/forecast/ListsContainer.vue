<template>
  <div class="lists-container">
    <List v-for="list in lists" :key="list.id" :list="list" />
  </div>
</template>

<script>
import List from '@/components/leads-index/List'

export default {
  name: 'ListsContainer',
  props: {
    lists: {
      type: Array,
      required: true,
    },
  },
  components: {
    List,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lists-container {
  @include standard-border();
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
}
</style>
