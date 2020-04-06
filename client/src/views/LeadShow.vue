<template>
  <div class="lead-show">
    <NavBar />
    <div class="page-content">
      <div class="left-pane">
        <img
          class="left-pane-screenshot"
          src="@/assets/images/screenshots/lead-show-left.png"
          alt="screenshot"
        />
      </div>
      <div class="center-pane">
        <LeadBanner :lead="lead" />
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
  background-color: #fafafa;
}

.page-content {
  overflow-x: scroll;
  flex-grow: 1;
  display: flex;
  flex-flow: row;
}

.left-pane {
  width: 21%;
  min-width: 294.75px;
  padding-top: 2%;
  padding-right: 1%;
  display: flex;
  flex-flow: row;
  // justify-content: center;

  .left-pane-screenshot {
    width: 243px;
    height: 773px;
    display: block;
    margin-left: auto;
  }
}

.center-pane {
  width: 54%;
  min-width: 795.5px;
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
  // border-top: solid 1px #f2f2f3;
  display: inline-block;
}

.right-pane {
  width: 25%;
  min-width: 335.5px;
  box-sizing: border-box;
  padding: 2% 1% 1% 1%;
}
</style>
