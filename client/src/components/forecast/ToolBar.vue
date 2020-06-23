<template>
  <div class="toolbar">
    <KPIs :repFilterState="repFilterState" />
    <div class="filter-container">
      <FilterByRep :repFilterState="repFilterState" @toggle-active-rep="emitToggleActiveRep" />
    </div>
  </div>
</template>

<script>
import FilterByRep from '@/components/shared/FilterByRep'
import KPIs from './_KPIs'

export default {
  name: 'ForecastToolBar',
  components: { FilterByRep, KPIs },
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
  },
  methods: {
    emitToggleActiveRep(repID) {
      this.$emit('toggle-active-rep', repID)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.toolbar {
  @include disable-text-select();
  @include standard-border();
  background-color: $white;
  width: 78%;
  height: auto;
  display: flex;
  flex-flow: column;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}

.filter-container {
  height: auto;
  margin: 1.5rem 0;
}
</style>
