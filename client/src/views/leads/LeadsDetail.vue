<template>
  <PageLoadingSVG v-if="loading" />
  <div v-else class="page">
    <div class="page__left-nav-bar">
      <ToolBar
        :lead="lead"
        :lists="lists"
        :contacts="contacts"
        :files="files"
        @updated-rating="updateRating"
        @updated-amount="updateAmount"
      />
    </div>
    <div class="page__main-content-area">
      <LeadBanner
        :lead="lead"
        @lead-reset="resetLead"
        @lead-released="releaseLead"
        @lead-claimed="claimLead"
      />
      <div v-if="lead" class="container">
        <LeadActions :lead="lead" />
      </div>
      <div class="container" style="margin: 2rem 0">
        <PinnedNotes
          :primaryDescription="lead.primaryDescription"
          :secondaryDescription="lead.secondaryDescription"
          @updated-primary-description="updatePrimaryDescription"
          @updated-secondary-description="updateSecondaryDescription"
        />
      </div>
      <div class="item-list">
        <div class="item-list__header">
          <span class="item-list__title">History</span>
        </div>

        <ActivityLogItem v-for="log in history.list" :key="log.id" :log="log" />

        <button
          class="primary-button"
          @click="addHistoryPage"
          v-if="history.pagination.hasNextPage"
          style="margin: 1rem"
        >Load More</button>
      </div>
    </div>

    <div class="page__right-panel">
      <LeadInsights :insights="insights" />
    </div>
  </div>
</template>

<script>
import ToolBar from '@/components/leads-detail/ToolBar'
import LeadBanner from '@/components/leads-detail/LeadBanner'
import LeadActions from '@/components/shared/LeadActions'
import PinnedNotes from '@/components/leads-detail/PinnedNotes'
import LeadInsights from '@/components/shared/LeadInsights'

import CollectionManager from '@/services/collectionManager'
import Lead from '@/services/leads'
import LeadActivityLog from '@/services/leadActivityLogs'
import List from '@/services/lists'
import Contact from '@/services/contacts'
import File from '@/services/files'

import ActivityLogItem from './_ActivityLogItem'

const EDIT_STATE = 'create'
const VIEW_STATE = 'view'

export default {
  name: 'LeadsDetail',
  props: ['id'],
  components: {
    ToolBar,
    LeadBanner,
    LeadActions,
    PinnedNotes,
    LeadInsights,
    ActivityLogItem,
  },
  data() {
    return {
      loading: false,
      lead: null,
      editState: EDIT_STATE,
      viewState: VIEW_STATE,
      lists: CollectionManager.create({
        ModelClass: List,
        filters: {
          byLead: this.id,
        },
      }),
      contacts: CollectionManager.create({
        ModelClass: Contact,
        filters: {
          byLead: this.id,
        },
      }),
      files: CollectionManager.create({
        ModelClass: File,
        filters: {
          byLead: this.id,
        },
      }),
      history: CollectionManager.create({
        ModelClass: LeadActivityLog,
        filters: {
          lead: this.id,
        },
      }),
      insights: null,
    }
  },
  async created() {
    Promise.all([
      this.retrieveLead(),
      this.lists.refresh(),
      this.contacts.refresh(),
      this.files.refresh(),
    ]).then(res => {
      this.lead = res[0]
      this.lists = res[1]
      this.contacts = res[2]
      this.files = res[3]
      this.loading = false
    })

    // Start polling for history
    // TODO: If this starts failing for any reason, it will start pumping out
    //       error messages, so we might want to clear or extend the interval
    //       if that happens.
    this.pollingInterval = setInterval(this.refreshHistory, 2000)
  },
  destroyed() {
    clearInterval(this.pollingInterval)
  },
  methods: {
    refreshHistory() {
      this.history.refresh()

      LeadActivityLog.api
        .getInsights({
          filters: {
            lead: this.id,
          },
        })
        .then(result => {
          this.insights = result
        })
    },
    addHistoryPage() {
      // TODO: This conflicts with polling, so we'll have to figure
      //       out how to handle that. For now, we disable polling
      //       if the user loads the next page, because they are
      //       looking for something old, not new.
      clearInterval(this.pollingInterval)
      this.history.addNextPage()
    },
    retrieveLead() {
      this.loading = true
      return Lead.api.retrieve(this.id)
    },
    updatePrimaryDescription(description) {
      let patchData = { primary_description: description }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    updateSecondaryDescription(description) {
      let patchData = { secondary_description: description }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    updateRating(rating) {
      let patchData = { rating }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    updateAmount(amount) {
      let patchData = { amount }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    resetLead() {
      let patchData = {
        status: null,
        amount: 0,
        forecast: null,
      }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = Object.assign(this.lead, lead)
        let message = `<div>Success! Lead reset.</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 4000,
        })
      })
    },
    claimLead() {
      Lead.api.claim(this.lead.id).then(() => {
        this.lead.claimedBy = this.$store.state.user.id
        let message = `<div>Lead claimed!</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 2000,
        })
      })
    },
    releaseLead() {
      Lead.api.unclaim(this.lead.id).then(() => {
        let message = `<div>Success! Lead released.</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 4000,
        })
        this.$router.push({ name: 'LeadsIndex' })
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
@import '@/styles/layout';
@import '@/styles/sidebars';
@import '@/styles/variables';
@import '@/styles/forms';
</style>
