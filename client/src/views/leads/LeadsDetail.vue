<template>
  <div v-if="loading" class="page">
    <ComponentLoadingSVG style="margin-top: 5rem;" />
  </div>
  <div v-else class="page">
    <div class="page__left-nav-bar">
      <!--        -->
      <SideNavToolbar>
        <template v-slot:trigger>
          <span
            class="toggle-icon"
            @click="$store.commit('TOGGLE_SIDE_TOOLBAR_NAV', !showToolbarNav)"
          >
            <div class="filter__button" v-show="!$store.state.showToolbarNav">
              <img class="filter__image" src="@/assets/images/logo.png" />
              <div class="filter__text">At a Glance</div>
            </div>
          </span>
        </template>
        <template v-slot:toolbar>
          <LeadInsights v-if="showToolbarNav && selectedToolbarView == 'insights'" :lead="lead" />
          <ToolBar
            v-if="showToolbarNav && selectedToolbarView == 'details'"
            :lead="lead"
            :lists="lists"
            :leadContacts="contacts"
            @updated-rating="updateRating"
            @updated-amount="updateAmount"
            @updated-expected-close-date="updateExpectedCloseDate"
            @updated-title="updateTitle"
          />
          <LeadCustomFields
            v-if="showToolbarNav && selectedToolbarView == 'custom-fields'"
            :lead="lead"
          />
        </template>
      </SideNavToolbar>
    </div>
    <div class="page__main-content-area-with-panel">
      <div class="lead-header">
        <h3>{{ lead.title }}</h3>
      </div>
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
          >History</div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': activityTabSelected === EMAILS }"
            @click="activityTabSelected = EMAILS"
          >Emails</div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': activityTabSelected === MESSAGES }"
            @click="activityTabSelected = MESSAGES"
          >Messages</div>

          <div class="check-email-btn" v-if="activityTabSelected === EMAILS && isEmailConnected">
            <button
              class="primary-button"
              @click="() => $refs.Emails.refresh()"
              :disabled="$refs.Emails && $refs.Emails.threads.refreshing"
            >Check for Mail</button>
          </div>

          <div class="history-search-container" v-if="activityTabSelected === HISTORY">
            <form @submit.prevent="onSearchHistory">
              <input v-model="historySearchTerm" placeholder="Search" />
            </form>
          </div>

          <div class="history-menu" v-if="activityTabSelected === HISTORY">
            <DropDownMenu
              @selectedItem="moreActionsAction"
              :right="10"
              :items="[
                { key: 'Expand All', value: 'expandAll' },
                { key: 'Collapse All', value: 'collapseAll' },
              ]"
            >
              <template v-slot:dropdown-trigger="{ toggle }">
                <svg @click="toggle" class="dd-icon" viewBox="0 0 24 20">
                  <use xlink:href="@/assets/images/more_horizontal.svg#more" />
                </svg>
              </template>
            </DropDownMenu>
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
          <template v-if="!isEmailConnected">
            <div>
              <span class="muted">
                <span
                  class="muted"
                >Please Enable Email Integration to use this feature in your settings</span>
              </span>
            </div>
          </template>
          <LeadEmails v-else :lead="lead" ref="Emails" />
        </div>
        <div v-show="activityTabSelected === MESSAGES" class="box__content">
          <LeadMessages :lead="lead" ref="Messages" />
        </div>
      </div>
    </div>
    <!-- 
    <div class="page__right-panel">
      
    </div>-->
  </div>
</template>

<script>
import ToolBar from '@/components/leads-detail/ToolBar'
import LeadCustomFields from '@/components/leads-detail/LeadCustomFields'
import LeadBanner from '@/components/leads-detail/LeadBanner'
import LeadActions from '@/components/shared/LeadActions'
import PinnedNotes from '@/components/leads-detail/PinnedNotes'
import LeadInsights from '@/components/shared/LeadInsights'
import DropDownMenu from '@/components/forms/DropDownMenu'
import SideNavToolbar from '@/components/navigation/SideNavToolbar'

import CollectionManager from '@/services/collectionManager'
import Lead from '@/services/leads'
import List from '@/services/lists'
import Contact from '@/services/contacts'
import Forecast from '@/services/forecasts'
import LeadActivityLog from '@/services/leadActivityLogs'

import LeadHistory from './_LeadHistory'
import LeadEmails from './_LeadEmails'
import LeadMessages from './_LeadMessages'
import { mapGetters } from 'vuex'
const HISTORY = 'HISTORY'
const EMAILS = 'EMAILS'
const MESSAGES = 'MESSAGES'
const EDIT_STATE = 'create'
const VIEW_STATE = 'view'

export default {
  name: 'LeadsDetail',
  props: ['id'],
  components: {
    ToolBar,
    LeadCustomFields,
    LeadBanner,
    LeadActions,
    PinnedNotes,
    LeadInsights,
    LeadHistory,
    LeadEmails,
    DropDownMenu,
    LeadMessages,
    SideNavToolbar,
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
      MESSAGES,
      activityTabSelected: HISTORY,
      showHistoryMenu: false,
      expandedHistoryItems: [],
      historySearchTerm: '',
      activityLogLoading: false,
      selectedToolbarView: 'details',
      history: CollectionManager.create({
        ModelClass: LeadActivityLog,
        filters: {
          lead: this.id,
          exclude: LeadActivityLog.types.LEAD_ACTIVITY_LOG_EXCLUDE.join(','),
        },
      }),
    }
  },
  computed: {
    ...mapGetters(['showToolbarNav']),
    isEmailConnected() {
      return !!this.$store.state.user.emailConnected
    },
    isTextConnected() {
      return !!this.$store.state.user.textConnected
    },
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
    toggleSideToolbar(option) {
      this.selectedToolbarView = option

      if (!this.showToolbarNav) {
        this.$store.commit('TOGGLE_SIDE_TOOLBAR_NAV', true)
      }
    },
    moreActionsAction(selected) {
      // TODO: PB Change this to be static with an enum type list (django style) 07/20

      if (selected == 'expandAll') {
        this.expandAllHistoryItems()
      }
      if (selected == 'collapseAll') {
        this.collapseAllHistoryItems()
      }
    },
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
    updatePrimaryDescription(primaryDescription) {
      Lead.api.update(this.lead.id, { primaryDescription }).then(lead => {
        this.lead = lead
      })
    },
    updateSecondaryDescription(secondaryDescription) {
      Lead.api.update(this.lead.id, { secondaryDescription }).then(lead => {
        this.lead = lead
      })
    },
    updateRating(rating) {
      Lead.api.update(this.lead.id, { rating }).then(lead => {
        this.lead = lead
      })
    },
    updateAmount(amount) {
      Lead.api.update(this.lead.id, { amount }).then(lead => {
        this.lead = lead
      })
    },
    updateExpectedCloseDate(expectedCloseDate) {
      const tzOffset = new Date().getTimezoneOffset()
      expectedCloseDate = `${expectedCloseDate}T${tzOffset / 60}:00`
      Lead.api.update(this.lead.id, { expectedCloseDate }).then(lead => {
        this.lead = lead
      })
    },
    updateTitle(title) {
      Lead.api.update(this.lead.id, { title }).then(lead => {
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
        expectedCloseDate: null,
        // Custom fields:
        companySize: null,
        industry: null,
        competitor: null,
        competitorDescription: null,
        geographyAddress: null,
        geographyAddressComponents: {},
        type: null,
        custom: null,
        /* NOTE (Bruno):
         reset_flag is used to discern if this was a lead-reset event or not,
         since a reset-event is actually a PATCH to /leads with default values decided client-side. */
        resetFlag: true,
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
@import '@/styles/mixins/buttons';

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
.toggle-icon {
  &:hover {
    cursor: pointer;
  }
}
.dd-icon {
  width: 20px;
  height: 15px;
  fill: #484a6e;
  &:hover {
    cursor: pointer;
  }
}
.lead-header {
  text-align: center;
  margin-bottom: 2rem;
}
.tooltip-icon {
  margin-bottom: 0.5rem;
}
.cloud-svg {
  height: 1.2rem;
  padding: 0.1rem;
  margin-right: 1rem;
}
.building-svg {
  height: 1.4rem;
  padding: 0 0.3rem;
}

.filter {
  &__button {
    @include secondary-button();
    margin-left: 1rem;
    width: 9rem;
  }
  &__text {
    font-weight: bold;
    margin-left: 1rem;
    font-size: 1rem;
  }
  &__image {
    height: 1.8rem;
    color: $dark-green;
  }
}
</style>
