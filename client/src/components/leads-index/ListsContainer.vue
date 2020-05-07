<template>
  <div class="lists-container">
    <List v-for="list in lists" :key="list.id" :list="list" />
    <CustomList :collection="leadsWithoutList" :title="'No List'" />
    <CustomList :collection="allLeads" :title="'All Leads'" />
    <CreateList @list-created="emitListCreated" />
  </div>
</template>

<script>
import List from '@/components/shared/List'
import CustomList from '@/components/leads-index/CustomList'
import CreateList from '@/components/leads-index/CreateList'

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
    CreateList,
  },
  methods: {
    emitListCreated(list) {
      this.$emit('list-created', list)
    },
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
