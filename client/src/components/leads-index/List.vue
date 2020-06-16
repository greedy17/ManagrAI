<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :class="{ open: showLeads, closed: !showLeads }">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title">{{ list.title }}</span>
      <span class="list-length">{{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
      <span class="icon">
        <svg
          width="50px"
          height="50px"
          class="icon"
          viewBox="0 0 30 30"
          v-if="isOwner"
          @click.stop="$emit('delete-list', list.id)"
        >
          <use xlink:href="@/assets/images/svg-repo.svg#remove" />
        </svg>
      </span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <ComponentLoadingSVG v-if="trueList.refreshing" />
      <template v-else>
        <div v-if="trueList.list.length" class="list-leads__row bulk-row">
          <span class="list-leads__row__action icon">
            <Checkbox :checked="allLeadsSelected" @checkbox-clicked="toggleAllSelected" />
          </span>
          <span
            class="list-leads__row__lead"
            :style="{ marginLeft: '1rem', display: 'flex', flexFlow: 'row', alignItems: 'center' }"
          >
            <span>
              Select All
            </span>
            <button class="bulk-action-button" v-if="!noLeadsSelected" @click="onBulkAction">
              Take Action
            </button>
            <button class="bulk-action-button" :style="{ visibility: 'hidden' }" v-else>
              Hidden
            </button>
            <Modal v-if="modal.isOpen" dimmed @close-modal="onCloseModal" :includeMargin="false">
              <BulkLeadActions
                :leads="Object.values(selectedLeads)"
                @bulk-move-success="onBulkMoveSuccess"
                @bulk-custom-action-success="onCloseModal"
              />
            </Modal>
          </span>
        </div>
        <div :key="lead.id" class="list-leads__row" v-for="lead in trueList.list">
          <span class="list-leads__row__action icon">
            <Checkbox
              :checked="!!selectedLeads[lead.id]"
              @checkbox-clicked="toggleSelectedLead(lead)"
            />
          </span>
          <span class="list-leads__row__lead">
            <Lead :key="lead.id" :lead="lead" />
          </span>
        </div>
        <span v-if="trueList.list.length <= 0" class="no-items-message">No Leads On List</span>
      </template>
      <LoadMoreButton
        v-if="!trueList.refreshing && !!trueList.pagination.next"
        class="load-more-button"
        :collection="trueList"
      />
    </div>
  </div>
</template>

<script>
import LeadModel from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
import Lead from '@/components/leads-index/Lead'
import List from '@/services/lists'
import LoadMoreButton from '@/components/shared/LoadMoreButton'
import Checkbox from '@/components/leads-new/CheckBox'
import BulkLeadActions from '@/components/leads-index/BulkLeadActions'

export default {
  name: 'List',
  props: {
    list: {
      // the prop 'list' is a shell: it only includes id, title, and leadCount. It is used to retrieve the trueList
      type: Object,
      required: true,
    },
    isOwner: {
      // determines if CRUD is available
      type: Boolean,
      default: false,
    },
    leadFilters: {
      type: Object,
      default: () => {},
    },
  },
  components: {
    Lead,
    LoadMoreButton,
    BulkLeadActions,
    Checkbox,
  },
  watch: {
    leadFilters: {
      deep: true,
      async handler() {
        this.madeInitialRetrieval = false
        this.showLeads = false
      },
    },
  },
  data() {
    return {
      loading: false,
      showLeads: false,
      madeInitialRetrieval: false,
      trueList: CollectionManager.create({
        ModelClass: LeadModel,
        filters: { byList: this.list.id, ...this.leadFilters },
      }),
      selectedLeads: {},
      modal: {
        isOpen: false,
      },
    }
  },
  methods: {
    // async removeFromList(leads, listId) {
    //   try {
    //     this.loading = true
    //     await List.api.removeFromList(leads, listId)
    //     this.trueList.refresh()

    //     this.list.leadCount = this.list.leadCount - 1
    //   } finally {
    //     this.loading = false
    //   }
    // },
    onBulkAction() {
      this.modal.isOpen = true
    },
    toggleSelectedLead(lead) {
      if (this.selectedLeads[lead.id]) {
        let copy = { ...this.selectedLeads }
        delete copy[lead.id]
        this.selectedLeads = copy
      } else {
        this.selectedLeads = { ...this.selectedLeads, [lead.id]: lead }
      }
    },
    toggleAllSelected() {
      if (this.allLeadsSelected) {
        this.selectedLeads = {}
      } else {
        this.selectedLeads = this.trueList.list.reduce((acc, lead) => {
          acc[lead.id] = lead
          return acc
        }, {})
      }
    },
    toggleLeads() {
      if (!this.madeInitialRetrieval) {
        // do not filter by user on lists
        this.trueList.filters = { byList: this.list.id, ...this.leadFilters }
        delete this.trueList.filters.byUser
        this.trueList.refresh().then(() => {
          this.madeInitialRetrieval = true
        })
      }
      this.showLeads = !this.showLeads
    },
    onCloseModal() {
      this.selectedLeads = {}
      this.modal.isOpen = false
    },
    onBulkMoveSuccess() {
      this.$emit('refresh-lists')
    },
  },
  computed: {
    numOfLeads() {
      return this.list.leadCount
    },
    allLeadsSelected() {
      return Object.keys(this.selectedLeads).length == this.trueList.list.length
    },
    noLeadsSelected() {
      return !Object.keys(this.selectedLeads).length
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.list-header {
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

.open {
  border: 2px solid $off-white;
}

.closed {
  border: 2px solid $white;
}

.icon {
  height: 1.625rem;
  width: 1.625rem;
  display: block;
  cursor: pointer;
}

.list-title {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}

.list-length {
  align-self: center;
  margin-left: 20%;
  margin-right: auto;
}

.list-leads {
  margin-left: 1%;
  margin-right: 1%;
  padding-top: 0.5rem;
  &__row {
    display: flex;
    flex-direction: row;
    align-items: center;

    &__lead {
      flex: 1;
    }
  }
}

.load-more-button {
  margin: 0.5rem auto;
}

.no-items-message {
  font-weight: bold;
  align-self: center;
  width: 25%;
  margin-left: 0.75rem;
}

.bulk-row {
  margin-bottom: 1rem;
  display: flex;
  flex-flow: row;
  justify-content: center;
  height: 2.5rem;
}

.bulk-action-button {
  @include primary-button;
  margin-left: 1rem;
}
</style>
