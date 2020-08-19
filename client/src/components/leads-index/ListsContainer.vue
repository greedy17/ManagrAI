<template>
  <div>
    <div class="lists-container">
      <div v-if="!loading" class="tab-content">
        <!-- 
          This set of lists contains custom created lists by a user and will populate the count based on that list
          if the total count is not yet available, the total count becomes available when the user toggles the list
        -->
        <List
          @delete-list="emitDeleteList(list.id, index)"
          v-for="(list, index) in listsCollection.list"
          :collection="leadsFromList"
          :key="index"
          :title="list.title"
          @get-leads="onGetLeads($event, list.id)"
          @refresh-collections="$emit('refresh-collections')"
          :leadCount="list.leadCount"
          :isOwner="true"
        />
        <!-- 
          This set of lists contains all opportunities and ones not on lists by a user and will populate the count based on that list
          if the total count of the collection
        -->
        <List
          :collection="noListLeadsCollection"
          key="No List"
          title="No List"
          @refresh-collections="$emit('refresh-collections')"
          :leadCount="noListLeadsCollection.pagination.totalCount"
        />
        <List
          :collection="allLeadsCollection"
          key="All Opportunities"
          title="All Opportunities"
          @refresh-collections="$emit('refresh-collections')"
          :leadCount="allLeadsCollection.pagination.totalCount"
        />
        <CreateList @list-created="emitListCreated" />
      </div>
      <div v-else class="tab-content">
        <ComponentLoadingSVG :style="{ marginTop: '5vh', marginBottom: '5vh' }" />
      </div>
    </div>
    <Pagination
      v-if="!listsCollection.refreshing"
      style="margin-top: 0.5rem;"
      :collection="listsCollection"
      :model="'List'"
      @start-loading="startPaginationLoading()"
    />
  </div>
</template>

<script>
import List from '@/components/leads-index/List'

import CreateList from '@/components/leads-index/CreateList'

import LeadModel from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
import Pagination from '@/components/shared/Pagination'

import { paginationMixin } from '@/services/pagination'

export default {
  name: 'ListsContainer',
  mixins: [paginationMixin],
  components: {
    List,
    CreateList,
    Pagination,
  },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      required: false,
      default: null,
    },
    listsCollection: {
      type: Object,
      required: true,
    },
    noListLeadsCollection: {
      type: Object,
      required: true,
    },
    allLeadsCollection: {
      type: Object,
      required: true,
    },
    showCreateNew: {
      type: Boolean,
      default: false,
    },
    filters: {
      type: Object,
      default: () => {},
    },
    isOwner: {
      // determines if CRUD is available
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      leadsFromList: CollectionManager.create({
        ModelClass: LeadModel,
        filters: {},
      }),
    }
  },
  methods: {
    async onGetLeads(show, listId) {
      if (show) {
        this.leadsFromList.filters = {
          byList: listId,
          byRating: this.filters.byRating ? this.filters.byRating : null,
          byStatus: this.filters.byStatus ? this.filters.byStatus : null,
        }
      }

      await this.leadsFromList.refresh()
    },
    emitDeleteList(listId, i) {
      this.$emit('delete-list', { id: listId, index: i })
    },
    emitListCreated(list) {
      this.$emit('list-created', list)
    },
    updateActiveTab(index) {
      this.activeTab = index
      let selected = this.viewTabs[this.activeTab]

      switch (selected) {
        case 'List View':
          this.listView = true
          break
        case 'Opportunity View':
          this.listView = false
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.lists-container {
  @include standard-border();
  background-color: $white;
  padding-top: 1vh;
  padding-bottom: 1vh;
}
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

.actions {
  min-width: 48rem;
  width: 100%;
  min-height: 21rem;
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
}

.actions-tab-headers {
  height: 3rem;
  display: flex;
  flex-flow: row;
  width: 100%;
  margin-bottom: 1rem;

  .header {
    @include pointer-on-hover();
  }
}

.action-tab-content {
  flex-grow: 1;
  padding: 2vh;
  display: flex;
  flex-flow: row;
}
.container-header {
  @include disable-text-select();
  @include pointer-on-hover();
  @include base-font-styles();
  display: flex;
  flex-flow: row;
  align-items: center;
  margin: 1vh 1%;
  padding-left: 1%;
  height: 3rem;
  font-size: 14px;
  line-height: 1.14;
  color: $main-font-gray;
}

.no-items-message {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}
</style>
