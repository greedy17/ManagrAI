<template>
  <div class="lists-container">
    <List v-for="list in lists" :key="list.id" :list="list" />
    <CustomList :collection="leadsWithoutList" :title="'No List'" />
    <CustomList :collection="allLeads" :title="'All Leads'" />
  </div>
</template>

<script>
import List from '@/components/leads-index/List'
import CustomList from '@/components/leads-index/CustomList'

export default {
  name: 'ListsContainer',
  props: {
    lists: {
      type: Array,
      required: true,
    },
    leadsWithoutList: {
      type: Object,
    },
    allLeads: {
      type: Object,
    },
  },
  components: {
    List,
    CustomList,
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
