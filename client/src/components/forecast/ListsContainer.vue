<template>
  <div class="lists-container">
    <List :key="lists['50/50'].title" :list="lists['50/50']" />
    <List :key="lists['STRONG'].title" :list="lists['STRONG']" />
    <List :key="lists['VERBAL'].title" :list="lists['VERBAL']" />
    <List :key="lists['FUTURE'].title" :list="lists['FUTURE']" />
    <List :key="lists['UNFORECASTED'].title" :list="lists['UNFORECASTED']" />
  </div>
</template>

<script>
import List from '@/components/forecast/List'

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
