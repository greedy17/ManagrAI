<template>
  <div v-if="loading" class="page">
    <ComponentLoadingSVG style="margin-top: 5rem;" />
  </div>
  <div v-else class="page">
    <div class="page__left-nav-bar">
      <ToolBar
        :lead="lead"
        :lists="lists"
        :leadContacts="contacts"
        @updated-rating="updateRating"
        @updated-amount="updateAmount"
        @updated-title="updateTitle"
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

      <!-- Lead History and Emails -->
      <div class="box" style="box-sizing: border-box;">
        <div class="box__tab-header">
          <div
            class="box__tab"
            :class="{ 'box__tab--active': activityTabSelected === HISTORY }"
            @click="
              () => {
                activityTabSelected = HISTORY
              }
            "
          >
            History
          </div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': activityTabSelected === EMAILS }"
            @click="
              () => {
                activityTabSelected = EMAILS
              }
            "
          >
            Email
          </div>

          <div class="check-email-btn" v-if="activityTabSelected === EMAILS">
            <button
              class="primary-button"
              @click="() => $refs.Emails.refresh()"
              :disabled="$refs.Emails && $refs.Emails.threads.refreshing"
            >
              Check for Mail
            </button>
          </div>

          <div class="history-search-container" v-if="activityTabSelected === HISTORY">
            <form @submit.prevent="onSearchHistory">
              <input v-model="historySearchTerm" placeholder="Search" />
            </form>
          </div>

          <div class="history-menu" v-if="activityTabSelected === HISTORY">
            <img
              class="icon"
              src="@/assets/images/more_horizontal.svg"
              @click="showHistoryMenu = !showHistoryMenu"
            />
            <div v-if="showHistoryMenu" class="menu">
              <p class="option" @click="expandAllHistoryItems">Expand All</p>
              <p class="option" @click="collapseAllHistoryItems">Collapse All</p>
            </div>
          </div>
        </div>

        <div v-show="activityTabSelected === HISTORY" class="box__content">
          <LeadHistory
            :lead="lead"
            ref="History"
            :history="history"
            @toggle-history-item="toggleHistoryItem"
            :expandedHistoryItems="expandedHistoryItems"
            :activityLogLoading="activityLogLoading"
          />
        </div>

        <div v-show="activityTabSelected === EMAILS" class="box__content">
          <LeadEmails :lead="lead" ref="Emails" />
        </div>
      </div>
    </div>

    <div class="page__right-panel">
      <LeadInsights :lead="lead" />
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
import List from '@/services/lists'
import Contact from '@/services/contacts'
import Forecast from '@/services/forecasts'
import LeadActivityLog from '@/services/leadActivityLogs'

import LeadHistory from './_LeadHistory'
import LeadEmails from './_LeadEmails'

const HISTORY = 'HISTORY'
const EMAILS = 'EMAILS'
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
    LeadHistory,
    LeadEmails,
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
      insights: null,

      // Past Activity Area
      HISTORY,
      EMAILS,
      activityTabSelected: HISTORY,
      showHistoryMenu: false,
      expandedHistoryItems: [],
      historySearchTerm: '',
      activityLogLoading: false,
      history: CollectionManager.create({
        ModelClass: LeadActivityLog,
        filters: {
          lead: this.id,
        },
      }),
    }
  },
  async created() {
    Promise.all([this.retrieveLead(), this.lists.refresh(), this.contacts.refresh()]).then(res => {
      this.lead = res[0]
      this.lists = res[1]
      this.contacts = res[2]
      this.loading = false
    })
  },
  methods: {
    onSearchHistory() {
      this.history.filters.search = this.historySearchTerm
      // Can not use history.refreshing because that will interfere with the polling
      this.activityLogLoading = true
      this.history.refresh().finally(() => {
        this.activityLogLoading = false
      })
    },
    expandAllHistoryItems() {
      this.expandedHistoryItems = this.history.list.map(h => h.id)
      this.showHistoryMenu = false
    },
    collapseAllHistoryItems() {
      this.expandedHistoryItems = []
      this.showHistoryMenu = false
    },
    toggleHistoryItem(id) {
      if (this.expandedHistoryItems.includes(id)) {
        this.expandedHistoryItems = this.expandedHistoryItems.filter(i => i != id)
      } else {
        this.expandedHistoryItems = [...this.expandedHistoryItems, id]
      }
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
    updateTitle(title) {
      let patchData = { title }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    resetLead() {
      let forecastPatchData = {
        lead: this.lead.id,
        forecast: 'NA',
      }

      let leadPatchData = {
        status: null,
        amount: 0,
        rating: 1,
      }

      Forecast.api
        .update(this.lead.forecast, forecastPatchData)
        .then(() => {
          return Lead.api.update(this.lead.id, leadPatchData)
        })
        .then(lead => {
          this.lead = lead
          let message = `<div>Success! Opportunity reset.</div>`
          this.$Alert.alert({
            type: 'success',
            message,
            timeout: 3000,
          })
        })
    },
    claimLead() {
      Lead.api.claim(this.lead.id).then(() => {
        this.lead.claimedBy = this.$store.state.user.id
        let message = `<div>Opportunity claimed!</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 3000,
        })
      })
    },
    releaseLead() {
      Lead.api.unclaim(this.lead.id).then(() => {
        let message = `<div>Success! Opportunity released.</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 3000,
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

.check-email-btn {
  flex: 1 1 0%;
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  justify-content: center;
}

.history-menu {
  flex: 1 1 0%;
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  justify-content: center;

  margin-right: 1rem;

  .icon {
    @include pointer-on-hover();
    opacity: 0.4;
  }

  .menu {
    position: absolute;
    z-index: 1083;
    margin-top: 3.5rem;
    background-color: $soft-gray;
    width: 6rem;
    padding: 0 1rem;
    border-radius: 3px;

    .option {
      @include pointer-on-hover();
    }
  }
}

.history-search-container {
  display: flex;
  flex-flow: row;
  align-items: center;
  width: 20rem;
  margin-left: 20rem;
  box-sizing: border-box;

  form {
    width: inherit;
    input {
      @include input-field;
      width: inherit;
    }
  }
}
</style>
