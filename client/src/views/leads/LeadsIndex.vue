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
      <ToolBar class="toolbar" @update-filter="updateFilters" :currentRatingFilter="ratingFilter" />
    </div>
    <div class="lists-container-pane">
      <ListsContainer
        title="My Lists"
        :leads="myLeads"
        :lists="myLists.list"
        @list-created="addListToCollection"
        @toggle-onlist="applyMyLeadsOnListFilter"
        :showCreateNew="true"
        :loading="myLists.refreshing || myLeads.refreshing"
        @delete-list="deleteList"
        :isOwner="true"
      />
      <ListsContainer
        title="Other Lists"
        :lists="lists.list"
        :leads="leads"
        @list-created="addListToCollection"
        @toggle-onlist="applyLeadsOnListFilter"
        :loading="leads.refreshing || lists.refreshing"
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
      myLists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byUser: this.$store.state.user.id,
        },
      }),
      lists: CollectionManager.create({
        ModelClass: List,
        filters: {
          // for this filter by adding the (-) minus symbol to a filter you can exclude it from the filter
          byUser: `-${this.$store.state.user.id}`,
        },
      }),
      myLeads: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byUser: this.$store.state.user.id,
          onList: true,
        },
      }),
      leads: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          // for this filter by adding the (-) minus symbol to a filter you can exclude it from the filter
          byUser: `-${this.$store.state.user.id}`,
          onList: true,
        },
      }),
    }
  },
  created() {
    this.refreshCollections()
  },
  computed: {
    isCurrentRoute() {
      return this.$route.name == 'LeadsIndex'
    },
    currentFilters() {
      // all filters should be the same across the collections
      return this.lists.filters
    },
    isLoading() {
      return (
        this.lists.refreshing ||
        this.myLists.refreshing ||
        this.leads.refreshing ||
        this.myLeads.refreshing
      )
    },
  },
  methods: {
    async deleteList(listInfo) {
      this.myLists.refreshing = true

      await List.api.deleteList(listInfo.id)
      // nested component wont react to splice
      this.$set(this.myLists, 'lists', this.myLists.list.splice(listInfo.index, 1))
    },
    refreshCollections() {
      let promises = [
        this.lists.refresh(),
        this.myLists.refresh(),
        this.leads.refresh(),
        this.myLeads.refresh(),
        //this.leadsWithoutList.refresh(),
        //this.allLeads.refresh(),
      ]
      Promise.all(promises).then(() => {
        this.loading = false
      })
    },
    toggleView() {
      this.$router.push({ name: 'Forecast' })
    },
    addListToCollection(list) {
      this.lists.list.unshift(list)
    },
    async applyMyLeadsOnListFilter(val) {
      this.myLeads.filters['onList'] = val
      await this.myLeads.refresh()
    },
    async applyLeadsOnListFilter(val) {
      this.leads.filters['onList'] = val
      await this.leads.refresh()
    },
    updateFilters(filter) {
      if (this.lists.filters[filter.key] == filter.value) {
        filter.value = null
      }
      // only update if there is a change
      // all collections should have the same filters so only
      // need one source of truth
      // if a collection does not have a filter
      // in its API filter class it will be removed on the request
      // components wont react to changes in obj[key] value
      // alt could have created a new list and set it to that
      //https://vuejs.org/v2/guide/reactivity.html#Change-Detection-Caveats
      this.$set(this.lists.filters, filter.key, filter.value)
      this.$set(this.myLists.filters, filter.key, filter.value)
      this.$set(this.leads.filters, filter.key, filter.value)
      this.$set(this.myLeads.filters, filter.key, filter.value)

      this.refreshCollections()
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
