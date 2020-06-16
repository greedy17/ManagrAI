<template>
  <div class="lists-container">
    <span class="container-header" v-if="title">{{ title.toUpperCase() }}</span>
    <div class="actions-tab-headers section-shadow">
      <ActionTabHeader
        v-for="(tab, index) in viewTabs"
        :key="tab"
        :active="index === activeTab"
        :index="index"
        @update-active-tab="updateActiveTab"
        class="header"
      >
        {{ tab }}
      </ActionTabHeader>
    </div>
    <div v-if="!loading" class="tab-content">
      <div v-if="!listView" class="view-toggle-container">
        <div class="checkbox-container">
          <span class="left" :class="{ bold: !onList }">No List</span>
          <ToggleCheckBox
            class="checkbox"
            :checked="onList"
            @toggle-on-list="onList = !onList"
            :eventToEmit="toggleEvent"
          />
          <span class="right" :class="{ bold: onList }">On List</span>
        </div>
        <span class="centered">
          {{
            onList
              ? `${onListLeadsCollection.pagination.totalCount} ${
                  onListLeadsCollection.pagination.totalCount == 1 ? 'Lead' : 'Leads'
                }`
              : `${noListLeadsCollection.pagination.totalCount} ${
                  noListLeadsCollection.pagination.totalCount == 1 ? 'Lead' : 'Leads'
                }`
          }}
        </span>
      </div>

      <div v-if="listView">
        <template v-if="listsCollection.list.length > 0">
          <List
            :isOwner="isOwner"
            @delete-list="emitDeleteList($event, index)"
            @remove-from-list="$emit('remove-from-list', $event)"
            v-for="(list, index) in listsCollection.list"
            :key="list.id"
            :list="list"
            :leadFilters="listsCollection.filters"
            @refresh-lists="listsCollection.refresh()"
          />
          <LoadMoreButton
            v-if="!listsCollection.refreshing && !!listsCollection.pagination.next"
            class="load-more-button"
            :collection="listsCollection"
          />
        </template>
        <template v-else>
          <span class="no-items-message">No Lists to show here</span>
        </template>
        <CreateList v-if="showCreateNew && listView" @list-created="emitListCreated" />
      </div>
      <div v-if="!listView">
        <template>
          <template v-if="onList && onListLeadsCollection.list.length > 0">
            <Lead v-for="lead in onListLeadsCollection.list" :key="lead.id" :lead="lead" />
            <LoadMoreButton
              v-if="!onListLeadsCollection.refreshing && !!onListLeadsCollection.pagination.next"
              class="load-more-button"
              :collection="onListLeadsCollection"
            />
          </template>
          <template v-else-if="!onList && noListLeadsCollection.list.length > 0">
            <Lead v-for="lead in noListLeadsCollection.list" :key="lead.id" :lead="lead" />
            <LoadMoreButton
              v-if="!noListLeadsCollection.refreshing && !!noListLeadsCollection.pagination.next"
              class="load-more-button"
              :collection="noListLeadsCollection"
            />
          </template>
          <template v-else>
            <span class="no-items-message">No Leads to show here</span>
          </template>
        </template>
      </div>
    </div>
    <div v-else class="tab-content">
      <ComponentLoadingSVG :style="{ marginTop: '5vh', marginBottom: '5vh' }" />
    </div>
  </div>
</template>

<script>
import List from '@/components/leads-index/List'
import CreateList from '@/components/leads-index/CreateList'
import Lead from '@/components/leads-index/Lead'
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'
import LoadMoreButton from '@/components/shared/LoadMoreButton'

const LISTVIEW = 'List View'
const LEADVIEW = 'Lead View'
const TOGGLEEVENT = 'toggle-on-list'

export default {
  name: 'ListsContainer',
  components: {
    List,
    CreateList,
    Lead,
    ActionTabHeader,
    ToggleCheckBox,
    LoadMoreButton,
  },
  data() {
    return {
      toggleEvent: TOGGLEEVENT,
      listView: true,
      onList: true,
      activeTab: 0,
      viewTabs: [LISTVIEW, LEADVIEW],
    }
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
    onListLeadsCollection: {
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
        case 'Lead View':
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

.load-more-button {
  margin: 0.5rem auto;
}
</style>
