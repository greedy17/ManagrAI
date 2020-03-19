<template>
  <div class="lead-show">
    <NavBar />
    <div class="page-content">
      <div class="left-pane">
        left pane
      </div>
      <div class="center-pane">
        <LeadBanner :lead="lead" />
        <div class="container">
          <LeadActions :lead="lead" />
        </div>
        <div class="container">
          <PinnedNotes />
        </div>
      </div>
      <div class="right-pane">
        <LeadInsights :lead="lead" />
      </div>
    </div>
  </div>
</template>

<script>
import { getSerializedLead } from '@/db.js'
import LeadBanner from '@/components/lead-show/LeadBanner'
import LeadActions from '@/components/shared/LeadActions'
import PinnedNotes from '@/components/lead-show/PinnedNotes'
import LeadInsights from '@/components/shared/LeadInsights'

export default {
  name: 'LeadShow',
  props: ['id'],
  components: {
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
}
</script>

<style lang="scss" scoped>
.lead-show {
  height: inherit;
  display: flex;
  flex-flow: column;
}

.page-content {
  flex-grow: 1;
  display: flex;
  flex-flow: row;
}

.left-pane {
  width: 16%;
}

.center-pane {
  width: 54%;
  padding: 2% 1% 1% 1%;

  .container {
    margin-top: 3%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.right-pane {
  width: 30%;
  box-sizing: border-box;
  padding: 2% 1% 1% 1%;
}
</style>
