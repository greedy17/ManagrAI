<template>
  <div class="list">
    <div class="list-header" @click="toggleLeads" :class="{ open: showLeads, closed: !showLeads }">
      <img class="icon" src="@/assets/images/toc.svg" alt="icon" />
      <span class="list-title">{{ title }}</span>
      <span class="list-length">
        {{ leadCount }}
        {{ leadCount > 1 || leadCount === 0 ? 'Opportunities' : 'Opportunity' }}
      </span>
      <span class="icon" v-if="isOwner">
        <svg
          width="50px"
          height="50px"
          class="icon"
          viewBox="0 0 30 30"
          v-if="isOwner"
          @click.stop="$emit('delete-list')"
        >
          <use xlink:href="@/assets/images/svg-repo.svg#remove" />
        </svg>
      </span>
    </div>
    <div class="list-leads" v-if="showLeads">
      <ComponentLoadingSVG v-if="collection.refreshing" />
      <template v-else>
        <div class="list-leads__row" v-if="collection.length">
          <span
            class="list-leads__row__lead"
            :style="{ display: 'flex', flexFlow: 'row', alignItems: 'center', height: '3rem' }"
          >
            <Checkbox
              @checkbox-clicked="toggleAllLeads"
              :checked="leadCount == checkedLeads.length"
            />

            <span :style="{ marginLeft: '0.75rem' }">Select All</span>
            <button class="bulk-action-button" v-if="checkedLeads.length > 0" @click="onBulkAction">
              Take Action
            </button>
            <button class="bulk-action-button" :style="{ visibility: 'hidden' }" v-else>
              Hidden
            </button>
            <Modal v-if="modal.isOpen" dimmed @close-modal="onCloseModal" :includeMargin="false">
              <BulkLeadActions
                :leads="checkedLeads"
                @bulk-move-success="onBulkMoveSuccess"
                @bulk-success="onCloseModal"
              />
            </Modal>
          </span>
        </div>
        <div :key="lead.id" class="list-leads__row" v-for="lead in collection">
          <span class="list-leads__row__lead">
            <LeadRow :key="lead.id" :lead="lead">
              <template v-slot:left>
                <Checkbox
                  :checked="!!~checkedLeads.findIndex(l => l == lead.id)"
                  @checkbox-clicked="toggleCheckedLead(lead.id)"
                />
              </template>
              <template v-slot:center>
                <div class="lead-items">
                  <span class="muted">
                    Expected Close By: <br />{{ lead.expectedCloseDate | dateShort }}</span
                  >
                  <span class="muted">
                    Last Action On:
                    <br />
                    {{ lead.lastActionTaken.actionTimestamp | timeAgo }} -
                    {{ lead.lastActionTaken.activity }}
                  </span>
                </div>
              </template>
              <template v-slot:right> </template>
            </LeadRow>
          </span>
        </div>
        <span v-if="collection.length <= 0" class="no-items-message">
          No Opportunities On List
        </span>
      </template>
      <!--       <LoadMoreButton
        v-if="!collection.refreshing && !!collection.pagination.next"
        class="load-more-button"
        :collection="collection"
      /> -->
    </div>
  </div>
</template>

<script>
import Lead from '@/components/leads-index/Lead'
import LoadMoreButton from '@/components/shared/LoadMoreButton'
import Checkbox from '@/components/leads-new/CheckBox'
import BulkLeadActions from '@/components/leads-index/BulkLeadActions'
import LeadRow from '@/components/shared/LeadRow'

export default {
  name: 'CustomList', // such as NoList and AllLeads
  props: {
    collection: {
      type: Array,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    leadCount: {
      type: Number,
      required: false,
    },
    isOwner: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    Lead,
    Checkbox,
    LoadMoreButton,
    BulkLeadActions,
    LeadRow,
  },
  data() {
    return {
      showLeads: false,

      checkedLeads: [],
      modal: {
        isOpen: false,
      },
    }
  },
  created() {},
  methods: {
    toggleLeads() {
      this.showLeads = !this.showLeads
      this.$emit('get-leads', this.showLeads)
    },
    onCloseModal() {
      this.checkedLeads = []
      this.modal.isOpen = false
    },
    onBulkMoveSuccess() {
      this.$emit('refresh-collections')
      this.onCloseModal()
    },
    onBulkAction() {
      this.modal.isOpen = true
    },
    toggleAllLeads() {
      this.checkedLeads = []
      this.checkedLeads = this.collection.list.map(l => l.id)
    },
    toggleCheckedLead(leadId) {
      let index = this.checkedLeads.findIndex(l => l == leadId)
      if (index != -1) {
        this.checkedLeads = this.checkedLeads.splice(index, 1)
      } else {
        this.checkedLeads.push(leadId)
      }
    },
  },
  computed: {},
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
    margin-top: 1rem;

    &__lead {
      flex: 1;
    }
  }
}
.lead-items {
  display: flex;
  align-items: center;
  > * {
    width: 150px;
  }
  .muted {
    font-size: 10px;
    color: black;
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
