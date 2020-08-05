<template>
  <div class="leads-index">
    <div class="toolbar-pane">
      <div class="view-toggle-container">
        <span class="left" :class="{ bold: isCurrentRoute }">Forecast</span>
        <ToggleCheckBox
          class="checkbox"
          :checked="!isCurrentRoute"
          @toggle-view="toggleView"
          :eventToEmit="'toggle-view'"
        />
        <span class="right" :class="{ bold: !isCurrentRoute }">Lists</span>
      </div>
      <ToolBar
        class="toolbar"
        :repFilterState="repFilterState"
        :triggerRefreshKPIs="triggerRefreshKPIs"
        @toggle-active-rep="toggleActiveRep"
        @select-all-reps="selectAllReps"
        @deselect-all-reps="deselectAllReps"
        @date-range-filter-change="dateRange => updateForecastCollections(dateRange)"
      />
    </div>
    <div class="lists-container-pane">
      <ComponentLoadingSVG v-if="loading" :style="{ marginTop: '10vh' }" />
      <div class="lists-container-message" v-else-if="!activeReps.length">
        No Representatives Selected!
      </div>
      <div class="lists-container-message" v-else-if="noResults">
        No Results!
      </div>
      <ListsContainer v-else :lists="lists" @trigger-refresh-kpis="triggerKPIs" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/forecast/ToolBar'
import ListsContainer from '@/components/forecast/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import Forecast from '@/services/forecasts'
import CollectionManager from '@/services/collectionManager'
import Pagination from '@/services/pagination'
import { dateRangeParamsFromPreset } from '@/services/dateRangeFilters'

function allRepsReducer(obj, id) {
  obj[id] = true
  return obj
}

export default {
  name: 'Forecast',
  components: {
    ToolBar,
    ToggleCheckBox,
    ListsContainer,
  },
  data() {
    return {
      loading: true,
      triggerRefreshKPIs: false,
      lists: {
        '50/50': CollectionManager.create({
          ModelClass: Forecast,
          filters: {
            forecast: Forecast.FIFTY_FIFTY,
            ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD),
          },
        }),
        STRONG: CollectionManager.create({
          ModelClass: Forecast,
          filters: {
            forecast: Forecast.STRONG,
            ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD),
          },
        }),
        VERBAL: CollectionManager.create({
          ModelClass: Forecast,
          filters: {
            forecast: Forecast.VERBAL,
            ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD),
          },
        }),
        FUTURE: CollectionManager.create({
          ModelClass: Forecast,
          filters: {
            forecast: Forecast.FUTURE,
            ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD),
          },
        }),
        UNFORECASTED: CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: Forecast.NA, ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD) },
        }),
        CLOSED: CollectionManager.create({
          ModelClass: Forecast,
          filters: {
            forecast: Forecast.CLOSED,
            ...dateRangeParamsFromPreset(Forecast.TODAY_ONWARD),
          },
        }),
      },
      repFilterState: {
        [this.$store.state.user.id]: true,
      },
    }
  },
  created() {
    this.updateForecastCollections()
  },
  methods: {
    triggerKPIs() {
      this.triggerRefreshKPIs = true
      setTimeout(() => (this.triggerRefreshKPIs = false), 0)
    },
    toggleView() {
      this.$router.push({ name: 'LeadsIndex' })
    },
    updateForecastCollections(dateRange) {
      this.resetPaginationOfCollections()
      if (dateRange) {
        this.applyDateRangeFilter(dateRange)
      }
      this.applyFilterByRep()
      this.refresh()
    },
    applyFilterByRep() {
      // turn array of rep IDs into a comma-delimited string of active reps
      let filterString = this.activeReps.join(',')
      // add string to filters for each of the collections
      Object.keys(this.lists).forEach(key => {
        this.lists[key].filters.byUser = filterString
      })
    },
    applyDateRangeFilter(dateRange) {
      Object.keys(this.lists).forEach(key => {
        this.lists[key].filters = {
          ...this.lists[key].filters,
          ...dateRangeParamsFromPreset(dateRange),
        }
      })
    },
    refresh() {
      this.loading = true
      // If no representatives selected, no Leads should be displayed.
      // Therefore, save a network hit.
      if (!this.activeReps.length) {
        this.loading = false
        return
      }
      let lists = [
        this.lists['50/50'].refresh(),
        this.lists['STRONG'].refresh(),
        this.lists['VERBAL'].refresh(),
        this.lists['FUTURE'].refresh(),
        this.lists['UNFORECASTED'].refresh(),
        this.lists['CLOSED'].refresh(),
      ]
      Promise.all(lists).then(() => {
        this.loading = false
      })
    },
    toggleActiveRep(repID) {
      // depending on state of this.repFilterState --> add or make false at that key
      // plainObject is used instead of an array because of O(1) lookup for <div class="rep" v-for.. />
      if (!this.repFilterState[repID]) {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: true })
      } else {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: false })
      }
      this.updateForecastCollections()
    },
    selectAllReps(repIDs) {
      let allRepsSelected = repIDs.reduce(allRepsReducer, {})
      this.repFilterState = allRepsSelected
      this.updateForecastCollections()
    },
    deselectAllReps() {
      this.repFilterState = {}
      this.updateForecastCollections()
    },
    resetPaginationOfCollections() {
      // When updating collection filter parameters,
      // may have an error if the pagination parameter stays at
      // page 2 but the new filter parameters can only yield a single page.
      // Therefore, reset pagination.
      this.lists['50/50'].pagination = Pagination.create()
      this.lists['STRONG'].pagination = Pagination.create()
      this.lists['VERBAL'].pagination = Pagination.create()
      this.lists['FUTURE'].pagination = Pagination.create()
      this.lists['UNFORECASTED'].pagination = Pagination.create()
      this.lists['CLOSED'].pagination = Pagination.create()
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name == 'Forecast'
    },
    userID() {
      return this.$store.state.user.id
    },
    activeReps() {
      return Object.keys(this.repFilterState).filter(repID => this.repFilterState[repID])
    },
    noResults() {
      for (let forecast in this.lists) {
        if (this.lists[forecast].list.length) {
          return false
        }
      }
      return true
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.leads-index {
  display: flex;
  flex-flow: row;
  padding-top: 2%;
}

.toolbar-pane {
  width: 17%;
  padding: 0% 1% 1% 1%;
  display: flex;
  flex-flow: column;
  background-color: $off-white;

  .toolbar {
    margin-left: auto;
  }
}

.view-toggle-container {
  @include base-font-styles();
  font-size: 0.825rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  width: 78%;
  margin: 0 0 1rem auto;

  .left,
  .right {
    width: 4rem;
    margin: 0 auto;
  }

  .left {
    text-align: right;
  }

  .checkbox {
    margin: 0 auto;
  }

  .bold {
    font-weight: bold;
  }
}

.lists-container-pane {
  width: 83%;
  padding: 0 2% 1% 1%;
  background-color: $off-white;
}

.lists-container-message {
  padding-top: 22vh;
  text-align: center;
  color: $gray;
  font-size: 1rem;
  font-weight: 600;
}
</style>
