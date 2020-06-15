<template>
  <div class="toolbar">
    <button class="new-lead" @click="routeToLeadsNew">
      New Lead
    </button>
    <div class="kpi-container">
      <div class="header section-shadow">
        Filter
      </div>
      <div class="filter-container">
        <FilterByRep :repFilterState="repFilterState" @toggle-active-rep="emitToggleActiveRep" />
      </div>
    </div>
  </div>
</template>

<script>
import FilterByRep from '@/components/shared/FilterByRep'

export default {
  name: 'ToolBar',
  components: {
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
  @include base-font-styles();
  color: $main-font-gray;
  line-height: 1.14;
  font-size: 1rem;
  font-weight: bold;
  height: 3rem;
  display: flex;
  flex-flow: column;
  justify-content: center;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

button.new-lead {
  @include primary-button();
  height: 2.5rem;
  width: 100%;
  font-size: 1rem;
}

.kpi-container {
  @include standard-border;
  margin-top: 1rem;
  background-color: $white;
}
.filter-container {
  height: auto;
  margin: 1.5rem 0;
}
</style>
