<template>
  <div class="leads-detail">
    <div class="left-pane">
      <ToolBar class="toolbar" :lead="lead" />
    </div>
    <div class="center-pane">
      <LeadBanner :lead="lead" @clicked-release="releaseLead" />
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
import { getSerializedLead } from '@/db.js'
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
      lead: {},
    }
  },
  created() {
    this.lead = getSerializedLead(this.id)
  },
  methods: {
    releaseLead() {
      Lead.api
        .unclaim(this.lead.id)
        .then(() => {
          let message = `<h2>Success!</h2><p>Lead released.</p>`
          this.$Alert.alert({
            type: 'success',
            message,
            timeout: 6000,
          })
          this.$router.push({ name: 'LeadsIndex' })
        })
        .catch(() => {
          let message = `<h2>Error...</h2><p>Please retry later.</p>`
          this.$Alert.alert({
            type: 'error',
            message,
            timeout: 6000,
          })
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
