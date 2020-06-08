<template>
  <PageLoadingSVG v-if="loading" />
  <div v-else class="leads-index">
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
        @toggle-active-rep="toggleActiveRep"
      />
    </div>
    <div class="lists-container-pane">
      <ListsContainer v-if="isRepFilterActive" :lists="lists" />
      <div v-else>
        No representative selected. Please select at least one via the side bar.
      </div>
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/forecast/ToolBar'
import ListsContainer from '@/components/forecast/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import Forecast from '@/services/forecasts'
import CollectionManager from '@/services/collectionManager'

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
      lists: {
        '50/50': CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: '50/50' },
        }),
        STRONG: CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: 'STRONG' },
        }),
        VERBAL: CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: 'VERBAL' },
        }),
        FUTURE: CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: 'FUTURE' },
        }),
        UNFORECASTED: CollectionManager.create({
          ModelClass: Forecast,
          filters: { forecast: 'NA' },
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
    toggleView() {
      this.$router.push({ name: 'LeadsIndex' })
    },
    updateForecastCollections() {
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
    refresh() {
      this.loading = true
      let lists = [
        this.lists['50/50'].refresh(),
        this.lists['STRONG'].refresh(),
        this.lists['VERBAL'].refresh(),
        this.lists['FUTURE'].refresh(),
        this.lists['UNFORECASTED'].refresh(),
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
    isRepFilterActive() {
      return !!this.activeReps.length
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
</style>
