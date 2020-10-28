<template>
  <div class="page">
    <div class="page__left-nav-bar">
      <SideNavToolbar>
        <template v-slot:trigger>
          <span
            class="toggle-icon"
            @click="$store.commit('TOGGLE_SIDE_TOOLBAR_NAV', !showToolbarNav)"
          >
            <div class="filter__button" v-show="!$store.state.showToolbarNav">
              <div class="filter__image">+</div>
              <div class="filter__text">Add Filter</div>
            </div>
          </span>
        </template>
        <template v-slot:toolbar>
          <ToolBar
            class="toolbar"
            @update-filter="updateFilters"
            :currentFilters="currentFilters"
            @delete-filters="deleteFilters"
          />
        </template>
      </SideNavToolbar>
    </div>
    <div class="page__main-content-area-with-panel">
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
      <ListsContainer
        :loading="loading"
        :noListLeadsCollection="myLeadsNoList"
        :allLeadsCollection="myLeadsAll"
        :listsCollection="myLists"
        @list-created="addListToCollection"
        :showCreateNew="true"
        @delete-list="deleteList"
        @remove-from-list="removeFromList"
        :isOwner="true"
        @refresh-collections="refreshCollections"
        :filters="currentFilters"
      />
    </div>
  </div>
</template>

<script>
import Button from '@thinknimble/button'

import ToolBar from '@/components/leads-index/ToolBar'
import ListsContainer from '@/components/leads-index/ListsContainer'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'
import SideNavToolbar from '@/components/navigation/SideNavToolbar'

import Lead from '@/services/leads'
import List from '@/services/lists'
import CollectionManager from '@/services/collectionManager'
import { mapGetters } from 'vuex'

export default {
  name: 'LeadsIndex',
  components: {
    ToolBar,
    ToggleCheckBox,
    ListsContainer,
    SideNavToolbar,
    Button,
  },
  data() {
    return {
      ratingFilter: null,
      myLists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byUser: this.$store.state.user.id,
          byReps: [this.$store.state.user.id],
          ordering: 'title',
        },
      }),
      myLeadsAll: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byReps: [this.$store.state.user.id],
        },
      }),
      myLeadsNoList: CollectionManager.create({
        ModelClass: Lead,
        filters: {
          onList: false,
          byReps: [this.$store.state.user.id],
        },
      }),
    }
  },
  created() {
    this.refreshCollections()
  },
  computed: {
    ...mapGetters(['showToolbarNav']),
    isCurrentRoute() {
      return this.$route.name == 'LeadsIndex'
    },
    currentFilters() {
      // all filters should be the same across the collections
      return this.myLists.filters
    },
    loading() {
      return this.myLists.refreshing || this.myLeadsAll.refreshing || this.myLeadsNoList.refreshing
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
      this.myLeadsAll.refresh()
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
      this.$set(this.myLeadsAll.filters, filter.key, filter.value)
      this.$set(this.myLeadsNoList.filters, filter.key, filter.value)

      this.refreshCollections()
    },
    deleteFilters() {
      const user = this.$store.state.user.id
      const clearedFilter = {
        byReps: [user],
        byUser: user,
      }

      this.myLists.filters = clearedFilter
      this.myLeadsAll.filters = clearedFilter
      this.myLeadsNoList.filters = clearedFilter

      this.refreshCollections()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';
@import '@/styles/layout';
@import '@/styles/mixins/buttons';

.view-toggle-container {
  @include base-font-styles();
  font-size: 0.825rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1rem 0;
  width: 10rem;

  .checkbox-container {
    display: flex;
    flex-flow: row;
    width: 20rem;
    justify-content: flex-start;
  }

  .left,
  .right {
    width: 4rem;
    margin: 0 1rem;
  }

  .left {
    text-align: right;
  }

  .checkbox {
    margin: 0 1rem;
  }

  .bold {
    font-weight: bold;
  }

  .centered {
    margin: 0 auto;
  }
}

.toggle-icon {
  &:hover {
    cursor: pointer;
  }
}

.filter {
  &__button {
    @include secondary-button();
    margin-left: 1rem;
    width: 9rem;

    // --theme-height: 2.5rem;
  }
  &__text {
    font-weight: bold;
    margin-left: 1rem;
    font-size: 1rem;
  }
  &__image {
    font-size: 1.8rem;
    color: $dark-green;
  }
}
</style>
