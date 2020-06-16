<template>
  <div class="leads-index">
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
      <ToolBar class="toolbar" @update-filter="updateFilters" :currentFilters="currentFilters" />
    </div>
    <div class="lists-container-pane">
      <ListsContainer
        :loading="loading"
        :noListLeadsCollection="myLeadsNoList"
        :onListLeadsCollection="myLeadsOnList"
        :listsCollection="myLists"
        @list-created="addListToCollection"
        :showCreateNew="true"
        @delete-list="deleteList"
        @remove-from-list="removeFromList"
        :isOwner="true"
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
      ratingFilter: null,
      myLists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byUser: this.$store.state.user.id,
          ordering: 'title',
        },
      }),
      myLeadsOnList: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byUser: this.$store.state.user.id,
          onList: true,
        },
      }),
      myLeadsNoList: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byUser: this.$store.state.user.id,
          onList: false,
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
      return this.myLists.filters
    },
    loading() {
      return (
        this.myLists.refreshing || this.myLeadsOnList.refreshing || this.myLeadsNoList.refreshing
      )
    },
  },
  methods: {
    async removeFromList(info) {
      // an object containing the lead as an array, listId, leadindex
      try {
        this.myLists.refreshing = true
        await List.api.removeFromList(info.leads, info.listId)
      } finally {
        this.myLists.refreshing = false
      }
    },
    async deleteList(listInfo) {
      this.myLists.refreshing = true

      await List.api.deleteList(listInfo.id)
      // nested component wont react to splice
      let newList = [...this.myLists.list]
      newList.splice(listInfo.index, 1)
      this.$set(this.myLists, 'list', newList)
      this.myLists.refreshing = false
    },
    refreshCollections() {
      this.myLists.refresh()
      this.myLeadsOnList.refresh()
      this.myLeadsNoList.refresh()
    },
    toggleView() {
      this.$router.push({ name: 'Forecast' })
    },
    addListToCollection(list) {
      let instance = List.fromAPI(list)
      this.myLists.list.unshift(instance)
    },
    updateFilters(filter) {
      if (this.myLists.filters[filter.key] == filter.value) {
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

      this.$set(this.myLists.filters, filter.key, filter.value)
      this.$set(this.myLeadsOnList.filters, filter.key, filter.value)
      this.$set(this.myLeadsNoList.filters, filter.key, filter.value)

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
