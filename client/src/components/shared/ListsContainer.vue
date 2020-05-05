<template>
  <div class="lists-container">
    <List v-for="list in lists" :key="list.id" :list="list" />
    <NoList :leads="leadsWithoutList" />
  </div>
</template>

<script>
import List from '@/components/leads-index/List'
import NoList from '@/components/leads-index/NoList'

export default {
  name: 'ListsContainer',
  props: ['lists', 'leadsWithoutList'],
  components: {
    List,
    NoList,
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
