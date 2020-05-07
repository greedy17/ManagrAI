<template>
  <div class="lists-container">
    <List :key="1" :title="'50/50'" :list="lists['50/50']" />
    <List :key="2" :title="'Strong'" :list="lists['STRONG']" />
    <List :key="3" :title="'Verbal'" :list="lists['VERBAL']" />
    <List :key="4" :title="'Future'" :list="lists['FUTURE']" />
    <List :key="5" :title="'Unforecasted'" :list="lists['UNFORECASTED']" />
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
