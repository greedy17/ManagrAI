<template>
  <div class="leads-index">
    <NavBar />
    <div class="page-content">
      <div class="toolbar-pane">
        <div class="view-toggle-container">
          <span :class="{ bold: view === FORECAST }">Forecast</span>
          <ToggleCheckBox
            :checked="view === LISTS"
            @toggle-view="toggleView"
            :eventToEmit="'toggle-view'"
          />
          <span :class="{ bold: view === LISTS }">Lists</span>
        </div>

        <ListsToolBar v-if="view === LISTS" class="toolbar" />
        <ForecastToolBar v-else class="toolbar" />
      </div>
      <div class="lists-container-pane">
        <ListsContainer v-if="view === LISTS" :lists="lists" />
        <ListsContainer v-else :lists="forecastLists" />
      </div>
    </div>
  </div>
</template>

<script>
import ListsToolBar from '@/components/leads-index/ListsToolBar'
import ForecastToolBar from '@/components/leads-index/ForecastToolBar'
import ListsContainer from '@/components/leads-index/ListsContainer'
import ToggleCheckBox from '@/components/leads-index/ToggleCheckBox'

import { getSerializedLists } from '@/db.js'

const LISTS = 'LISTS'
const FORECAST = 'FORECAST'

export default {
  name: 'LeadsIndex',
  components: {
    ListsToolBar,
    ForecastToolBar,
    ToggleCheckBox,
    ListsContainer,
  },
  data() {
    return {
      LISTS,
      FORECAST,
      view: LISTS,
      lists: null,
      forecastLists: null,
    }
  },
  created() {
    this.lists = getSerializedLists()
  },
  methods: {
    toggleView() {
      if (this.view === LISTS) {
        this.view = FORECAST
      } else {
        this.view = LISTS
      }
      //NOTE(Bruno 4-16-20): writing this here for now, when we get data from the API this is worth revisitng.
      if (this.forecastLists === null) {
        this.forecastLists = this.generateForecastLists()
      }
    },
    generateForecastLists() {
      //NOTE(Bruno 4-16-20): this is a very brute force / not optimal algorithm  ~ O(n^2).
      // When we have a backend maybe we can serialize there or we can think this over
      let bucketsObj = {}
      for (let i = 0; i < this.lists.length; ++i) {
        let currentList = this.lists[i]
        for (let j = 0; j < currentList.leads.length; ++j) {
          let currentLead = currentList.leads[j]
          if (bucketsObj[currentLead.forecast]) {
            bucketsObj[currentLead.forecast].push(currentLead)
          } else {
            bucketsObj[currentLead.forecast] = [currentLead]
          }
        }
      }
      return Object.keys(bucketsObj).map(bucketKey => ({
        title: bucketKey,
        leads: bucketsObj[bucketKey],
      }))
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.leads-index {
  min-height: 100vh;
  display: flex;
  flex-flow: column;
  background-color: $off-white;
}

.page-content {
  padding-top: 2%;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
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
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 0.825rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  justify-content: center;
  width: 78%;
  margin: 0 0 1rem auto;

  span {
    margin: 0 1rem;
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
