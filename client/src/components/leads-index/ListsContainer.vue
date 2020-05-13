<template>
  <div class="lists-container">
    <PageLoadingSVG v-if="loading" />
    <span class="container-header" v-if="title">{{ title.toUpperCase() }}</span>
    <div class="actions-tab-headers section-shadow">
      <ActionTabHeader
        v-for="(tab, index) in viewTabs"
        :key="tab"
        :active="index === activeTab"
        :index="index"
        @update-active-tab="updateActiveTab"
      >
        {{ tab }}
      </ActionTabHeader>
    </div>
    <div class="tab-content">
      <div v-if="!listView" class="view-toggle-container">
        <span class="left" :class="{ bold: !onList }">No List</span>
        <ToggleCheckBox
          class="checkbox"
          :checked="onList"
          @toggle-on-list="onList = !onList"
          :eventToEmit="toggleEvent"
        />
        <span class="right" :class="{ bold: onList }">On List</span>
      </div>
      <div v-if="listView">
        <template v-if="lists.length > 0">
          <List v-for="list in lists" :key="list.id" :list="list" />
          <!-- <CustomList v-if="leadsWithoutList" :collection="leadsWithoutList" :title="'No List'" />
      <CustomList v-if="allLeads" :collection="allLeads" :title="'All Leads'" /> -->
          <CreateList v-if="showCreateNew && listView" @list-created="emitListCreated" />
        </template>
        <template v-else>
          <span class="placeholder-message">No Lists to show here</span>
        </template>
      </div>
      <div v-if="!listView">
        <template v-if="leads.length > 0">
          <Lead v-for="lead in leads" :key="lead.id" :lead="lead" />
        </template>
        <template v-else>
          <span class="placeholder-message">No Leads to show here</span>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import List from '@/components/leads-index/List'
import CreateList from '@/components/leads-index/CreateList'
import Lead from '@/components/leads-index/Lead'
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import ToggleCheckBox from '@/components/shared/ToggleCheckBox'
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
  watch: {
    onList(cur, pre) {
      // toggles whether a user wants to view leads on or off a list
      if (pre != cur) {
        this.$emit('toggle-onlist', cur)
      }
    },
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
    lists: {
      type: Array,
      required: true,
      default: () => [],
    },

    leads: {
      type: Array,
      default: () => [],
    },
    leadsWithoutList: {
      type: Object,
      default: () => {},
    },
    allLeads: {
      type: Object,
      default: () => {},
    },
    showCreateNew: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
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
  justify-content: flex-start;
  width: 20%;
  margin: 1rem 0;

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

.placeholder-message {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}
</style>
