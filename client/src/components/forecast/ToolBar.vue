<template>
  <div class="toolbar">
    <KPIs
      :repFilterState="repFilterState"
      @date-range-filter-change="emitDateRangeFilterChange"
      :triggerRefreshKPIs="triggerRefreshKPIs"
    />

    <div class="filter section-shadow">
      <div class="filter-header" @click="expand">
        Filter by Representative
        <span class="icon__container">
          <svg
            v-if="!showRep"
            class="icon--unclicked"
            fill="black"
            width="24px"
            height="24px"
            viewBox="0 0 30 30"
          >
            <use xlink:href="@/assets/images/svg-repo.svg#caret" />
          </svg>
          <svg
            v-if="showRep"
            class="icon--clicked"
            fill="black"
            width="24px"
            height="24px"
            viewBox="0 0 30 30"
          >
            <use xlink:href="@/assets/images/svg-repo.svg#caret" />
          </svg>
        </span>
      </div>
    </div>
    <div class="filter-container" v-show="showRep" style="padding-top: 1rem;">
      <FilterByRep
        :repFilterState="repFilterState"
        @toggle-active-rep="emitToggleActiveRep"
        @select-all-reps="emitSelectAllReps"
        @deselect-all-reps="$emit('deselect-all-reps')"
      />
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
    triggerRefreshKPIs: {
      required: true,
      type: Boolean,
    },
  },
  data() {
    return {
      showRep: false,
    }
  },
  methods: {
    emitToggleActiveRep(repID) {
      this.$emit('toggle-active-rep', repID)
    },
    emitSelectAllReps(repIDs) {
      this.$emit('select-all-reps', repIDs)
    },
    emitDateRangeFilterChange(dateRange) {
      this.$emit('date-range-filter-change', dateRange)
    },
    expand() {
      this.showRep = !this.showRep
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
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  height: auto;
  display: flex;
  flex-flow: column;
  max-width: 15rem;
  margin-bottom: 2rem;
}

.toolbar,
.toolbar > * {
  @include base-font-styles();
  line-height: 1.14;
  color: $main-font-gray;
  font-size: 0.875rem;
}

.filter {
  .filter-header {
    height: 3rem;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0 10%;
    font-weight: normal;
    &:hover {
      cursor: pointer;
    }
  }
}

.icon {
  &__container {
    display: flex;
  }
  &--unclicked {
    transform: rotate(-90deg);
  }
  &--clicked {
    transform: rotate(90deg);
  }
}
</style>
