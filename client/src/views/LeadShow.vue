<template>
  <div class="lead-show">
    <NavBar />
    <div class="page-content">
      <div class="left-pane">
        left pane
      </div>
      <div class="center-pane">
        center
      </div>
      <div class="right-pane">
        <LeadInsights :lead="lead" />
      </div>
    </div>
  </div>
</template>

<script>
import { getSerializedLead } from '@/db.js'
import LeadInsights from '@/components/shared/LeadInsights'

export default {
  name: 'LeadShow',
  props: ['id'],
  components: {
    LeadInsights,
  },
  data() {
    return {
      lead: {},
    }
  },
  created() {
    this.list = getSerializedLead(this.id)
  },
}
</script>

<style scoped>
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
  flex-grow: 1;
}

.right-pane {
  width: 30%;
  box-sizing: border-box;
  padding: 2% 1% 1% 1%;
}
</style>
