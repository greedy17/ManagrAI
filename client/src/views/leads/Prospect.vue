<template>
  <PageLoadingSVG v-if="loading" />
  <div v-else class="prospect">
    <div class="toolbar-pane">
      <ToolBar :repFilterState="repFilterState" @toggle-active-rep="toggleActiveRep" />
    </div>
    <div class="lists-pane">
      <AccountsContainer :accounts="accountsWithLeads" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/prospect/ToolBar'
import AccountsContainer from '@/components/prospect/AccountsContainer'
import Account from '@/services/accounts'
import Lead from '@/services/leads'
import CollectionManager from '@/services/collectionManager'

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
      }),
      accountsWithLeads: [], // objects containing account info & collections of leads for account
      repFilterState: {},
    }
  },
  async created() {
    // get all of the accounts for this organization
    await this.accounts.refresh()
    // generate a collection for each retrieved account, to get its leads
    this.generateCollections()
    this.refreshCollections()
  },
  methods: {
    generateCollections() {
      // collections of leads filtered by account
      this.accountsWithLeads = this.accounts.list.map(this.generateAccountLeadsObject)
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
      // update byUser filter for each collection,
      this.applyFilterByRep()
      // refresh each collection
      let promises = this.accountsWithLeads.map(accountWithLeads =>
        accountWithLeads.collection.refresh(),
      )
      Promise.all(promises).then(() => {
        this.loading = false
      })
    },
    applyFilterByRep() {
      // turn array of rep IDs into a comma-delimited string of active reps
      let filterString = this.activeReps.join(',')
      // add string to filters for each of the collections
      Object.keys(this.accountsWithLeads).forEach(key => {
        this.accountsWithLeads[key].collection.filters.byUser = filterString
      })
    },
    toggleActiveRep(repID) {
      // depending on state of this.repFilterState --> add or make false at that key
      // plainObject is used instead of an array because of O(1) lookup for <div class="rep" v-for.. />
      if (!this.repFilterState[repID]) {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: true })
      } else {
        this.repFilterState = Object.assign({}, this.repFilterState, { [repID]: false })
      }
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
