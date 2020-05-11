<template>
  <PageLoadingSVG v-if="loading" />
  <div v-else class="leads-index">
    <div class="toolbar-pane">
      <div class="view-toggle-container">
        <span class="left" :class="{ bold: !isCurrentRoute }">Forecast</span>
        <ToggleCheckBox
          class="checkbox"
          :checked="isCurrentRoute"
          @toggle-view="toggleView"
          :eventToEmit="'toggle-view'"
        />
        <span class="right" :class="{ bold: isCurrentRoute }">Lists</span>
      </div>
      <ToolBar
        class="toolbar"
        @updated-rating-filter="updateRatingFilter"
        :currentRatingFilter="ratingFilter"
      />
    </div>
    <div class="lists-container-pane">
      <ListsContainer
        :lists="lists.list"
        :leadsWithoutList="leadsWithoutList"
        :allLeads="allLeads"
        @list-created="addListToCollection"
      />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/leads-index/ToolBar'
import ListsContainer from '@/components/leads-index/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'

import Lead from '@/services/leads'
import List from '@/services/lists'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'LeadsIndex',
  components: {
    ToolBar,
    ToggleCheckBox,
    ListsContainer,
  },
  data() {
    return {
      loading: true,
      ratingFilter: null,
      lists: CollectionManager.create({
        ModelClass: List,
      }),
      leadsWithoutList: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          onList: 'False',
        },
      }),
      allLeads: CollectionManager.create({
        ModelClass: Lead,
      }),
    }
  },
  created() {
    this.refreshCollections()
  },
  methods: {
    refreshCollections() {
      this.applyFiltersToCollections()
      let promises = [
        this.lists.refresh(),
        this.leadsWithoutList.refresh(),
        this.allLeads.refresh(),
      ]
      Promise.all(promises).then(() => {
        this.loading = false
      })
    },
    applyFiltersToCollections() {
      // apply lead-rating filter
      // this.lists.filters.rating = this.ratingFilter // filter structure pending (server-side WIP)
      this.leadsWithoutList.filters.rating = this.ratingFilter
      this.allLeads.filters.rating = this.ratingFilter
      // apply lead-status filter
      // ...
      // apply lead-forecast filter
      // ...
    },
    toggleView() {
      this.$router.push({ name: 'Forecast' })
    },
    addListToCollection(list) {
      this.lists.list.unshift(list)
    },
    updateRatingFilter(rating) {
      // if the current filter option was clicked, then remove the ratingFiler
      if (this.ratingFilter == rating) {
        this.ratingFilter = null
      } else {
        this.ratingFilter = rating
      }
      this.loading = true
      this.refreshCollections()
    },
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name == 'LeadsIndex'
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
