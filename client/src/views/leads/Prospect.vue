<template>
  <div class="prospect">
    <div class="toolbar-pane">
      <ToolBar
        :repFilterState="repFilterState"
        :unclaimedFilterState="unclaimedFilterState"
        :activeSearchTerm="toolbarSearchTerm"
        @toggle-active-rep="toggleActiveRep"
        @toggle-unclaimed="toggleUnclaimed"
        @search-filter="filterByLeadTitle"
        @clear-search-filter="filterByLeadTitle('')"
        @select-all-reps="selectAllReps"
        @deselect-all-reps="deselectAllReps"
      />
    </div>
    <div class="lists-pane">
      <AccountsContainer
        :accounts="accounts"
        :isFilteringActive="isFilteringActive"
        :leadFilters="leadLevelFilters"
      />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/prospect/ToolBar'
import AccountsContainer from '@/components/prospect/AccountsContainer'

import Account from '@/services/accounts'
import CollectionManager from '@/services/collectionManager'
import Pagination from '@/services/pagination'
import { objectToSnakeCase } from '@/services/utils'

function allRepsReducer(obj, id) {
  obj[id] = true
  return obj
}

export default {
  name: 'Prospect',
  components: {
    ToolBar,
    AccountsContainer,
  },
  data() {
    return {
      accounts: CollectionManager.create({
        ModelClass: Account,
        filters: {
          ordering: 'name',
        },
      }),
      repFilterState: {},
      unclaimedFilterState: false,
      toolbarSearchTerm: '',
      isFilteringActive: false,
    }
  },
  created() {
    this.accounts.refresh()
  },
  methods: {
    updateAccounts() {
      this.resetPagination()
      this.applyAccountLevelFilters()
      this.accounts.refresh()
    },
    resetPagination() {
      this.accounts.pagination = Pagination.create()
    },
    applyAccountLevelFilters() {
      if (this.byParamsIsRedundant) {
        this.isFilteringActive = false
        this.accounts.filters = { ...this.accounts.filters, byParams: null }
        return
      }

      this.isFilteringActive = true
      let params = {}
      if (this.unclaimedFilterState) {
        params = {
          representatives: null,
          onlyUnclaimed: true,
          searchTerm: this.toolbarSearchTerm ? this.toolbarSearchTerm : null,
        }
      } else {
        params = {
          representatives: this.activeReps,
          onlyUnclaimed: null,
          searchTerm: this.toolbarSearchTerm ? this.toolbarSearchTerm : null,
        }
      }
      this.accounts.filters = { ...this.accounts.filters, byParams: objectToSnakeCase(params) }
    },
    toggleActiveRep(repID) {
      // depending on state of this.repFilterState --> add or make false at that key
      // plainObject is used instead of an array because of O(1) lookup for <div class="rep" v-for.. />
      if (!this.repFilterState[repID]) {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: true })
      } else {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: false })
      }
      //  if filtering by rep, remove filter by unclaimed
      this.unclaimedFilterState = false
      this.updateAccounts()
    },
    toggleUnclaimed() {
      this.unclaimedFilterState = !this.unclaimedFilterState
      // if toggling unclaimed, be it on or off, reset filterByRep
      this.repFilterState = {}
      this.updateAccounts()
    },
    filterByLeadTitle(searchTerm) {
      this.toolbarSearchTerm = searchTerm
      this.updateAccounts()
    },
    selectAllReps(repIDs) {
      this.unclaimedFilterState = false
      let allRepsSelected = repIDs.reduce(allRepsReducer, {})
      this.repFilterState = allRepsSelected
      this.updateAccounts()
    },
    deselectAllReps() {
      this.unclaimedFilterState = false
      this.repFilterState = {}
      this.updateAccounts()
    },
  },
  computed: {
    activeReps() {
      return Object.keys(this.repFilterState).filter(repID => this.repFilterState[repID])
    },
    leadLevelFilters() {
      return {
        isClaimed: this.unclaimedFilterState ? 'False' : null,
        byUser: this.activeReps.join(','),
        search: this.toolbarSearchTerm ? this.toolbarSearchTerm : null,
      }
    },
    byParamsIsRedundant() {
      // if all aspects of accounts.filters.byParams are null/empty,then it is a redundant filter
      return !this.unclaimedFilterState && !this.toolbarSearchTerm.length && !this.activeReps.length
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.prospect {
  display: flex;
  flex-flow: row;
  padding-top: 2%;
  padding-bottom: 2%;
}

.toolbar-pane {
  width: 18vw;
  display: flex;
  flex-flow: column;
  align-items: center;
}

.lists-pane {
  width: 82vw;
}
</style>
