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
        @clear-search-filter="clearSearchFilter"
        @select-all-reps="selectAllReps"
        @deselect-all-reps="deselectAllReps"
      />
    </div>
    <div class="lists-pane">
      <AccountsContainer
        v-if="!loading"
        :accounts="accountsWithLeads"
        :accountsCollection="accounts"
        :isFilteringActive="isFilteringActive"
        @on-left-arrow-click="getPage(accounts.pagination.page - 1)"
        @on-page-click="getPage"
        @on-right-arrow-click="getPage(accounts.pagination.page + 1)"
      />
      <ComponentLoadingSVG v-else :style="{ marginTop: '10vh' }" />
    </div>
  </div>
</template>

<script>
import VueScrollTo from 'vue-scrollto'
import ToolBar from '@/components/prospect/ToolBar'
import AccountsContainer from '@/components/prospect/AccountsContainer'
import Account from '@/services/accounts'
import Lead from '@/services/leads'
import CollectionManager from '@/services/collectionManager'
import { apiErrorHandler } from '@/services/api'

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
      loading: true,
      accounts: CollectionManager.create({
        ModelClass: Account,
        filters: {
          ordering: 'name',
        },
      }),
      accountsWithLeads: [], // objects containing account info & collections of leads for account
      repFilterState: {},
      unclaimedFilterState: false,
      toolbarSearchTerm: '',
      isFilteringActive: false,
    }
  },
  async created() {
    // get all of the accounts for this organization
    await this.accounts.refresh()
    // generate a collection for each retrieved account, to get its leads
    this.accountsWithLeads = this.generateCollections(this.accounts.list)
    this.refreshCollections()
  },
  methods: {
    generateCollections(list) {
      // collections of leads filtered by account
      return list.map(this.generateAccountLeadsObject)
    },
    generateAccountLeadsObject(account) {
      let collection = CollectionManager.create({
        ModelClass: Lead,
        filters: {
          byAccount: account.id,
        },
      })
      return {
        account,
        collection,
      }
    },
    refreshCollections() {
      this.loading = true
      // update filters for each collection,
      this.applyFilters()
      // update isFilteringActive state, for filtering-result purposes
      this.isFilteringActive = !!(
        this.unclaimedFilterState ||
        this.toolbarSearchTerm.length ||
        this.activeReps.length
      )
      // refresh each collection
      let promises = this.accountsWithLeads.map(accountWithLeads =>
        accountWithLeads.collection.refresh(),
      )
      Promise.all(promises).then(() => {
        this.loading = false
      })
    },
    applyFilters() {
      if (this.unclaimedFilterState) {
        Object.keys(this.accountsWithLeads).forEach(key => {
          this.accountsWithLeads[key].collection.filters = {
            ...this.accountsWithLeads[key].collection.filters,
            byUser: null,
            isClaimed: 'False',
            search: this.toolbarSearchTerm ? this.toolbarSearchTerm : null,
          }
        })
      } else {
        // turn array of rep IDs into a comma-delimited string of active reps
        let filterString = this.activeReps.join(',')
        // add string to filters for each of the collections
        Object.keys(this.accountsWithLeads).forEach(key => {
          this.accountsWithLeads[key].collection.filters = {
            ...this.accountsWithLeads[key].collection.filters,
            byUser: filterString,
            isClaimed: null,
            search: this.toolbarSearchTerm ? this.toolbarSearchTerm : null,
          }
        })
      }
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
      this.refreshCollections()
    },
    getPage(pageNumber) {
      // this custom method must be used instead of CollectionManager.refresh
      // because of the desired UX given the serialized data:
      // we must get the next page of accounts to then go through this next page and
      // fetch each account's first page of leads
      VueScrollTo.scrollTo('#nav', 0)
      this.loading = true

      let tempCollection = CollectionManager.create({
        ModelClass: Account,
      })

      tempCollection.pagination = {
        ...this.accounts.pagination,
        page: pageNumber,
      }
      tempCollection.filters = {
        ...this.accounts.filters,
      }

      tempCollection
        .refresh()
        .then(collection => {
          let tempAccountsWithLeads = this.generateCollections(collection.list)
          let promises = tempAccountsWithLeads.map(accountWithLeads =>
            accountWithLeads.collection.refresh(),
          )

          Promise.all(promises).then(() => {
            // here add tempAccountsWithLeads to this.accountsWithLeads
            this.accountsWithLeads = tempAccountsWithLeads
            this.accounts.pagination = collection.pagination
            this.loading = false
          })
        })
        .catch(error => {
          this.loading = false
          apiErrorHandler({ apiName: 'ProspectPage.getPage' })(error)
        })
    },
    toggleUnclaimed() {
      // if filtering by unclaimed, reset filterByRep
      this.unclaimedFilterState = !this.unclaimedFilterState
      this.repFilterState = {}
      this.refreshCollections()
    },
    filterByLeadTitle(searchTerm) {
      this.toolbarSearchTerm = searchTerm
      this.refreshCollections()
    },
    clearSearchFilter() {
      this.toolbarSearchTerm = ''
      this.refreshCollections()
    },
    selectAllReps(repIDs) {
      let allRepsSelected = repIDs.reduce(allRepsReducer, {})
      this.repFilterState = allRepsSelected
      this.refreshCollections()
    },
    deselectAllReps() {
      this.repFilterState = {}
      this.refreshCollections()
    },
  },
  computed: {
    activeReps() {
      return Object.keys(this.repFilterState).filter(repID => this.repFilterState[repID])
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
