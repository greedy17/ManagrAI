<template>
  <LoadingSVG v-if="loading" />
  <div v-else class="leads-detail">
    <div class="left-pane">
      <ToolBar class="toolbar" :lead="lead" @updated-rating="updateRating" />
    </div>
    <div class="center-pane">
      <LeadBanner
        :lead="lead"
        @lead-released="releaseLead"
        @updated-forecast="updateForecast"
        @updated-status="updateStatus"
      />
      <div class="container">
        <LeadActions :lead="lead" />
      </div>
      <div class="container">
        <PinnedNotes />
      </div>
      <div class="container">
        <img
          class="additional-information"
          src="@/assets/images/screenshots/AdditionalInformation.png"
          alt="screenshot"
        />
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

export default {
  name: 'LeadsDetail',
  props: ['id'],
  components: {
    ToolBar,
    LeadBanner,
    LeadActions,
    PinnedNotes,
    LeadInsights,
  },
  data() {
    return {
      loading: true,
      lead: null,
    }
  },
  created() {
    Lead.api.retrieve(this.id).then(lead => {
      this.lead = lead
      this.loading = false
    })
  },
  methods: {
    updateRating(rating) {
      let patchData = { rating }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    updateForecast(value) {
      alert('selected' + value + '(sever-side WIP)')
    },
    updateStatus(value) {
      let patchData = { status: value.toUpperCase() }
      Lead.api.update(this.lead.id, patchData).then(lead => {
        this.lead = lead
      })
    },
    releaseLead() {
      Lead.api.unclaim(this.lead.id).then(() => {
        let message = `<div>Success! Lead released.</div>`
        this.$Alert.alert({
          type: 'success',
          message,
          timeout: 6000,
        })
        this.$router.push({ name: 'LeadsIndex' })
      })
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
