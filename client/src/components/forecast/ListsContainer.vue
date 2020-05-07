<template>
  <div class="lists-container">
    <List :key="list.title" :list="list" />
    <List :key="list.title" :list="list" />
    <List :key="list.title" :list="list" />
    <List :key="list.title" :list="list" />
    <List :key="list.title" :list="list" />
  </div>
</template>

<script>
import List from '@/components/shared/List'

export default {
  name: 'ListsContainer',
  props: {
    lists: {
      type: Object,
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
