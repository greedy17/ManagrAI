<template>
  <div class="box">
    <div class="box__tab-header">
      <ActionTabHeader
        v-for="(tab, index) in tabs"
        :key="tab"
        :active="index === activeTab"
        :index="index"
        @update-active-tab="updateActiveTab"
      >
        {{ tab }}
      </ActionTabHeader>
      <div class="acting-on-leads">
        Acting on {{ leads.length }}
        {{ leads.length > 1 || leads.length === 0 ? 'Opportunities' : 'Opportunity' }}
      </div>
    </div>

    <div class="box__content">
      <div v-if="activeTab == 0">
        <ComponentLoadingSVG v-if="lists.refreshing" />
        <template v-else>
          Move all selected Opportunities to the following Lists:
          <div v-for="list in lists.list" :key="list.id" class="list-items">
            <span
              class="list-items__item__select"
              :style="{ display: 'flex', flexFlow: 'row', alignItems: 'center' }"
            >
              <Checkbox
                name="lists"
                @checkbox-clicked="toggleSelectedList(list)"
                :checked="!!selectedLists[list.id]"
              />
              <span class="list-items__item">{{ list.title }}</span>
            </span>
          </div>
          <h5>To remove opportunities from all lists, leave all checkboxes blank</h5>
          <div :style="{ display: 'flex', flexFlow: 'row' }">
            <button class="on-bulk-move" @click="onBulkMove">Bulk Move Opportunities</button>
          </div>
        </template>
      </div>
      <div v-if="activeTab == 1">
        <BulkNoteAction :leads="leads" />
      </div>
      <div v-if="activeTab == 2">
        <BulkCustomAction :leads="leads" />
      </div>
      <!-- <div v-if="activeTab == 3">Bulk Email</div> -->
    </div>
  </div>
</template>

<script>
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import CollectionManager from '@/services/collectionManager'
import List from '@/services/lists'
import Checkbox from '@/components/leads-new/CheckBox'
import BulkCustomAction from '@/components/leads-index/BulkCustomAction'
import BulkNoteAction from '@/components/leads-index/BulkNoteAction'

export default {
  name: 'BulkLeadActions',
  components: {
    ActionTabHeader,
    Checkbox,
    BulkCustomAction,
    BulkNoteAction,
  },
  props: {
    leads: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['Action', 'Note', 'Lists'],
      // for bulk movement:
      lists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byUser: this.$store.state.user.id,
          ordering: 'title',
        },
      }),
      selectedLists: {},
    }
  },
  created() {
    this.lists.refresh()
  },
  methods: {
    async updateActiveTab(index) {
      if (this.tabs[index] !== this.tabs[this.activeTab]) {
        this.activeTab = index
      }
    },
    toggleSelectedList(list) {
      if (this.selectedLists[list.id]) {
        let copy = { ...this.selectedLists }
        delete copy[list.id]
        this.selectedLists = copy
      } else {
        this.selectedLists = { ...this.selectedLists, [list.id]: list }
      }
    },
    onBulkMove() {
      let selectedLists = Object.keys(this.selectedLists)
      List.api.bulkUpdate(this.leads, selectedLists).then(() => {
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Opportunities moved!',
        })
        this.selectedLists = {}
        this.$emit('bulk-move-success')
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/containers';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/inputs';

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
  min-height: 3rem;
  display: flex;
  flex-flow: row;
}

.action-tab-content {
  flex: 1 auto;
  padding: 2vh;
  display: flex;
  flex-flow: row;
  overflow: scroll;
}
.list-items {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-y: scroll;
}
.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
}
.svg {
  fill: red;
  width: 30px;
  height: 30px;
}
.list-items__header {
  font-weight: bold;
}
.list-items__item,
.list-items__header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;

  > * {
    align-self: center;
    margin-left: 0.75rem;
    color: rgba($color: $main-font-gray, $alpha: 0.4);
    flex: 1;
  }
  &__content {
    color: rgba($color: $main-font-gray, $alpha: 1);
    flex: 2;
  }
}

.on-bulk-move {
  @include primary-button;
  margin-left: auto;
}

.acting-on-leads {
  margin: auto 2rem auto auto;
  color: $dark-green;
  font-weight: bold;
}
</style>
