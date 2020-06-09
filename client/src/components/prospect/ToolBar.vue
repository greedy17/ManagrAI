<template>
  <div class="toolbar">
    <button class="new-lead" @click="routeToLeadsNew">
      New Lead
    </button>
    <div class="kpi-container">
      <KPIs />
    </div>
    <div class="filter-container">
      <FilterByRep :repFilterState="repFilterState" @toggle-active-rep="emitToggleActiveRep" />
    </div>
  </div>
</template>

<script>
import KPIs from '@/components/prospect/KPIs'
import FilterByRep from '@/components/shared/FilterByRep'

export default {
  name: 'ToolBar',
  components: {
    KPIs,
    FilterByRep,
  },
  props: {
    repFilterState: {
      required: true,
      type: Object,
    },
  },
  methods: {
    routeToLeadsNew() {
      this.$router.push({ name: 'LeadsNew' })
    },
    emitToggleActiveRep(repID) {
      this.$emit('toggle-active-rep', repID)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
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

.header {
  display: flex;
  flex-flow: column;
  justify-content: center;
  height: 3rem;
  padding-left: 7%;
  font-weight: bold;
}

button.new-lead {
  @include primary-button();
  height: 2.5rem;
  width: 100%;
  font-size: 1rem;
}

.kpi-container {
  margin-top: 1rem;
}
.filter-container {
  height: auto;
  margin: 1.5rem 0;
}
</style>
