<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :class="{ open: showLeads, closed: !showLeads }">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title">{{ title }}</span>
      <span class="list-length">{{ numOfLeads }} {{ numOfLeads === 1 ? 'Lead' : 'Leads' }}</span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <ComponentLoadingSVG v-if="collection.refreshing" />
      <template v-else>
        <div class="list-leads__row" v-if="collection.list.length">
          <span
            class="list-leads__row__lead"
            :style="{ display: 'flex', flexFlow: 'row', alignItems: 'center', height: '3rem' }"
          >
            <Checkbox
              :style="{ marginLeft: '1rem' }"
              :checked="allLeadsSelected"
              @checkbox-clicked="toggleAllSelected"
            />

            <span :style="{ marginLeft: '0.75rem' }">Select All</span>
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
                @bulk-success="onCloseModal"
              />
            </Modal>
          </span>
        </div>
        <div :key="lead.id" class="list-leads__row" v-for="lead in collection.list">
          <span class="list-leads__row__lead">
            <Lead
              :key="lead.id"
              :lead="lead"
              :isSelected="!!selectedLeads[lead.id]"
              @checkbox-clicked="toggleSelectedLead(lead)"
            />
          </span>
        </div>
        <span v-if="collection.list.length <= 0" class="no-items-message">No Leads On List</span>
      </template>
      <LoadMoreButton
        v-if="!collection.refreshing && !!collection.pagination.next"
        class="load-more-button"
        :collection="collection"
      />
    </div>
  </div>
</template>

<script>
import Lead from '@/components/leads-index/Lead'
import LoadMoreButton from '@/components/shared/LoadMoreButton'
import Checkbox from '@/components/leads-new/CheckBox'
import BulkLeadActions from '@/components/leads-index/BulkLeadActions'

export default {
  name: 'CustomList', // such as NoList and AllLeads
  props: {
    collection: {
      type: Object,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
  components: {
    Lead,
    Checkbox,
    LoadMoreButton,
    BulkLeadActions,
  },
  data() {
    return {
      showLeads: false,
      selectedLeads: {},
      modal: {
        isOpen: false,
      },
    }
  },
  methods: {
    toggleLeads() {
      this.showLeads = !this.showLeads
    },
    onCloseModal() {
      this.selectedLeads = {}
      this.modal.isOpen = false
    },
    onBulkMoveSuccess() {
      this.$emit('refresh-collections')
      this.onCloseModal()
    },
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
        this.selectedLeads = this.collection.list.reduce((acc, lead) => {
          acc[lead.id] = lead
          return acc
        }, {})
      }
    },
  },
  computed: {
    numOfLeads() {
      return this.collection.pagination.totalCount
    },
    allLeadsSelected() {
      return Object.keys(this.selectedLeads).length == this.collection.list.length
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

.bulk-action-button {
  @include primary-button;
  margin-left: 1rem;
}
</style>
