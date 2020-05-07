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
      <ToolBar class="toolbar" />
    </div>
    <div class="lists-container-pane">
      <ListsContainer :lists="lists" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/forecast/ToolBar'
import ListsContainer from '@/components/forecast/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import Forecast from '@/services/forecasts'
import CollectionManager from '@/services/collectionManager'

// import { getSerializedLists } from '@/db.js'

export default {
  name: 'Forecast',
  components: {
    ToolBar,
    ToggleCheckBox,
    ListsContainer,
  },
  data() {
    return {
      lists: null,
    }
  },
  created() {
    // this.lists = getSerializedLists()
    // this.lists = this.generateForecastLists()
    let userID = this.$store.state.user.id
    CollectionManager.create({ ModelClass: Forecast, filters: { byUser: userID } })
      .refresh()
      .then(response => {
        console.log(response)
      })
  },
  methods: {
    toggleView() {
      this.$router.push({ name: 'LeadsIndex' })
    },
    // generateForecastLists() {
    //   //NOTE(Bruno 4-16-20): this is a very brute force / not optimal algorithm  ~ O(n^2).
    //   // When we have a backend maybe we can serialize there or we can think this over
    //   let bucketsObj = {}
    //   for (let i = 0; i < this.lists.length; ++i) {
    //     let currentList = this.lists[i]
    //     for (let j = 0; j < currentList.leads.length; ++j) {
    //       let currentLead = currentList.leads[j]
    //       if (bucketsObj[currentLead.forecast]) {
    //         bucketsObj[currentLead.forecast].push(currentLead)
    //       } else {
    //         bucketsObj[currentLead.forecast] = [currentLead]
    //       }
    //     }
    //   }
    //   return Object.keys(bucketsObj).map(bucketKey => ({
    //     title: bucketKey,
    //     leads: bucketsObj[bucketKey],
    //   }))
    // },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name == 'Forecast'
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
