<template>
  <div>
    <div class="lists-container">
      <div v-if="!loading" class="tab-content">
        <List
          :isOwner="isOwner"
          @delete-list="emitDeleteList($event, index)"
          @remove-from-list="$emit('remove-from-list', $event)"
          v-for="(list, index) in listsCollection.list"
          :key="list.id"
          :list="list"
          :leadFilters="listsCollection.filters"
          @refresh-collections="$emit('refresh-collections')"
        />
        <CustomList
          :collection="noListLeadsCollection"
          key="No List"
          title="No List"
          @refresh-collections="$emit('refresh-collections')"
        />
        <CustomList
          :collection="allLeadsCollection"
          key="All Opportunities"
          title="All Opportunities"
          @refresh-collections="$emit('refresh-collections')"
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
import CustomList from '@/components/leads-index/CustomList'
import CreateList from '@/components/leads-index/CreateList'
import Pagination from '@/components/shared/Pagination'

import { paginationMixin } from '@/services/pagination'

export default {
  name: 'ListsContainer',
  mixins: [paginationMixin],
  components: {
    List,
    CreateList,
    Pagination,
    CustomList,
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
    isOwner: {
      // determines if CRUD is available
      type: Boolean,
      default: false,
    },
  },

  methods: {
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

  .checkbox-container {
    display: flex;
    flex-flow: row;
    width: 20rem;
    justify-content: flex-start;
  }

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
