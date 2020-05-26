<template>
  <PageLoadingSVG v-if="loading" />
  <div v-else class="leads-detail">
    <Modal v-if="modal.isOpen" dimmed @close-modal="closeModal" :width="50">
      <CloseLead :lead="lead" />
    </Modal>
    <div class="left-pane">
      <ToolBar
        class="toolbar"
        :lead="lead"
        :lists="lists"
        :contacts="contacts"
        :files="files"
        @updated-rating="updateRating"
        @updated-amount="updateAmount"
      />
    </div>
    <div class="center-pane">
      <LeadBanner
        :lead="lead"
        @lead-reset="resetLead"
        @lead-released="releaseLead"
        @lead-claimed="claimLead"
        @updated-forecast="updateForecast"
        @updated-status="updateStatus"
      />
      <div v-if="lead" class="container">
        <LeadActions :lead="lead" />
      </div>
      <div class="container">
        <PinnedNotes
          :primaryDescription="lead.primaryDescription"
          :secondaryDescription="lead.secondaryDescription"
          @updated-primary-description="updatePrimaryDescription"
          @updated-secondary-description="updateSecondaryDescription"
        />
      </div>
      <!--  Hiding this as it is still WIP as requested by marcy pb 05/15/20
        
        <div class="container">
        <img
          class="additional-information"
          src="@/assets/images/screenshots/AdditionalInformation.png"
          alt="screenshot"
        />
      </div> -->

      <div class="container">
        <LeadActions v-if="lead" :state="viewState" :lead="lead" />
      </div>
    </div>
    <div class="right-pane">
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
import Lead from '@/services/leads'
import Forecast from '@/services/forecasts'
import CloseLead from '@/components/shared/CloseLead'
import CollectionManager from '@/services/collectionManager'
import List from '@/services/lists'
import Contact from '@/services/contacts'
import File from '@/services/files'

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
    CloseLead,
  },
  data() {
    return {
      loading: false,
      lead: null,
      modal: {
        isOpen: false,
      },
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
  },
  methods: {
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
    updateForecast(value) {
      if (this.lead.forecast) {
        // since forecast exists, patch forecast
        let patchData = {
          lead: this.lead.id,
          forecast: value,
        }
        Forecast.api.update(this.lead.forecastRef.id, patchData).then(response => {
          this.lead.forecastRef = response
          this.lead.forecast = response.id
        })
      } else {
        // since currently null, create forecast
        Forecast.api.create(this.lead.id, value).then(response => {
          this.lead.forecastRef = response
          this.lead.forecast = response.id
        })
      }
    },
    updateStatus(value) {
      if (value != 'CLOSED') {
        let patchData = { status: value }
        Lead.api.update(this.lead.id, patchData).then(lead => {
          this.lead = lead
        })
      } else {
        this.modal.isOpen = true
      }
    },
    resetLead() {
      let patchData = {
        status: null,
        amount: 0,
        forecast: null,
      }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
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
    closeModal() {
      this.modal.isOpen = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.leads-detail {
  display: flex;
  flex-flow: row;
}

.left-pane {
  width: 21%;
  min-width: 18.45rem;
  padding-top: 2%;
  padding-right: 1%;
  display: flex;
  flex-flow: row;

  .toolbar {
    width: 15.2rem;
    margin-left: auto;
  }
}

.center-pane {
  width: 54%;
  min-width: 49.75rem;
  padding: 2% 1% 1% 1%;

  .container {
    margin-top: 3%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.additional-information {
  width: 100%;
  display: inline-block;
}

.right-pane {
  width: 25%;
  min-width: 21rem;
  box-sizing: border-box;
  padding: 2% 1% 1% 1%;
}
</style>
